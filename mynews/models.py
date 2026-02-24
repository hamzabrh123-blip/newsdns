import uuid
import re
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
    
    category = models.CharField(max_length=100, blank=True, null=True) # Hindi name for display
    url_city = models.CharField(max_length=100, blank=True, null=True) # URL slug for the city/category
    
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
        # 1. DISTRICT, CATEGORY & URL_CITY LOGIC
        if self.district:
            d_val = str(self.district).strip()
            found_in_data = False
            for item in LOCATION_DATA:
                try:
                    # item[0]=EngID, item[1]=HindiName, item[2]=CitySlug
                    if len(item) >= 3 and str(item[0]).strip() == d_val:
                        self.category = item[1]  # Display ke liye Hindi (e.g. 'बलिया')
                        self.url_city = slugify(unidecode(item[2])) # URL ke liye English slug (e.g. 'ballia')
                        found_in_data = True
                        break
                except:
                    continue
            
            # Agar constants mein na mile toh district id ko hi slug bana do
            if not found_in_data:
                self.url_city = slugify(unidecode(d_val))
        else:
            # Agar district select nahi kiya (जैसे National news), toh hamesha 'news' url use hoga
            self.url_city = 'news'
            if not self.category:
                self.category = "Uttar Pradesh"

        # 2. SLUG LOGIC (News Title Slug)
        if not self.slug:
            # Title ko clean karke slug banana aur UUID add karna duplicate se bachne ke liye
            base_slug = slugify(unidecode(self.title))[:60]
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:6]}"

        # 3. PHOTO UPLOAD LOGIC (ImgBB upload)
        if self.image and not self.image_url:
            try:
                link = process_and_upload_to_imgbb(self)
                if link:
                    self.image_url = link
            except Exception as e:
                print(f"Image Upload Error: {e}")

        # 4. FINAL SAVE TO DATABASE
        super(News, self).save(*args, **kwargs)

        # 5. FACEBOOK SHARING LOGIC
        try:
            if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
                # Ensure photo is uploaded before sharing
                if self.image_url:
                    if post_to_facebook(self):
                        # Avoid recursion: use update() instead of save()
                        News.objects.filter(id=self.id).update(is_fb_posted=True)
                else:
                    print("FB Post Skipped: Image URL not ready yet.")
        except Exception as e:
            print(f"Facebook Posting Error: {e}")

    def __str__(self):
        return f"{self.title} | ({self.district})"
