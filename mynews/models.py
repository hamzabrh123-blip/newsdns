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
    
    category = models.CharField(max_length=100, blank=True, null=True, editable=False)
    url_city = models.CharField(max_length=100, blank=True, null=True, editable=False)
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
        # 1. District Logic
        if self.district:
            for item in LOCATION_DATA:
                if len(item) >= 3 and self.district == item[0]:
                    self.category = item[1]
                    self.url_city = item[2]
                    break
        
        # 2. Slug Logic
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))[:60]}-{str(uuid.uuid4())[:6]}"

        # 3. Pehle Base Save Karo (Iske bina ID nahi milti)
        super(News, self).save(*args, **kwargs)

        # 4. ImgBB & Facebook (ALAG SE AUR SAFE)
        try:
            needs_update = False
            
            # Sirf Image Upload
            if self.image and not self.image_url:
                img_link = process_and_upload_to_imgbb(self)
                if img_link:
                    self.image_url = img_link
                    needs_update = True

            # Sirf Facebook Share (Isse alag rakha hai)
            if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
                if post_to_facebook(self):
                    self.is_fb_posted = True
                    needs_update = True

            # Agar kuch change hua toh simple update chalao
            if needs_update:
                News.objects.filter(id=self.id).update(
                    image_url=self.image_url, 
                    is_fb_posted=self.is_fb_posted
                )
        except Exception:
            pass # Site nahi rukni chahiye chahe FB fail ho jaye

    def __str__(self):
        return self.title
