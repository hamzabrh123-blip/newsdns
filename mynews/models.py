import uuid
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from .constants import LOCATION_DATA 
from .utils import process_and_upload_to_imgbb, post_to_facebook

class News(models.Model):
    title = models.CharField(max_length=250)
    status = models.CharField(max_length=20, choices=[('Draft', 'Draft'), ('Published', 'Published')], default='Published')
    
    category = models.CharField(max_length=100, blank=True, null=True)
    url_city = models.CharField(max_length=100, blank=True, null=True)
    
    district = models.CharField(max_length=100, choices=[(x[0], x[1]) for x in LOCATION_DATA], blank=True, null=True)
    
    content = RichTextField(blank=True)
    image = models.ImageField(upload_to="news_pics/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    date = models.DateTimeField(default=now) 
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    is_important = models.BooleanField(default=False, verbose_name="Breaking News?")
    show_in_highlights = models.BooleanField(default=False, verbose_name="Top 5 Highlights?")
    meta_keywords = models.TextField(blank=True, null=True)
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Share to FB?")
    is_fb_posted = models.BooleanField(default=False)

    class Meta:
        db_table = 'mynews_news'
        verbose_name_plural = "News"

    def save(self, *args, **kwargs):
        # 1. DISTRICT & CATEGORY LOGIC
        if self.district:
            d_val = str(self.district).strip()
            for item in LOCATION_DATA:
                try:
                    if len(item) >= 3 and str(item[0]).strip() == d_val:
                        self.category = item[1]
                        self.url_city = item[2]
                        break
                except:
                    continue

        # 2. SLUG LOGIC
        if not self.id and not self.slug:
            self.slug = f"{slugify(unidecode(self.title))[:60]}-{str(uuid.uuid4())[:6]}"

        # 3. PHOTO UPLOAD LOGIC (Save से पहले ताकि image_url मिल जाए)
        # अगर नई फोटो अपलोड हुई है और image_url खाली है
        if self.image and not self.image_url:
            try:
                link = process_and_upload_to_imgbb(self)
                if link:
                    self.image_url = link
            except Exception as e:
                print(f"Image Upload Error: {e}")

        # 4. FINAL SAVE TO DATABASE
        super(News, self).save(*args, **kwargs)

        # 5. FACEBOOK SHARING LOGIC (Save के बाद)
        try:
            # अब यहाँ self.image_url हमेशा भरा हुआ मिलेगा अगर ImgBB सफल रहा है
            if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
                if self.image_url: # पक्का करें कि इमेज लिंक मौजूद है
                    if post_to_facebook(self):
                        # recursion से बचने के लिए update इस्तेमाल किया
                        self.__class__.objects.filter(id=self.id).update(is_fb_posted=True)
                else:
                    print("FB Post Skipped: Image URL not ready.")
        except Exception as e:
            print(f"Facebook Posting Error: {e}")

    def __str__(self):
        return self.title
