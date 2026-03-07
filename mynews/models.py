import uuid
import os
from django.db import models, transaction
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from ckeditor.fields import RichTextField
from .constants import LOCATION_DATA 
from .utils import process_and_upload_to_imgbb, post_to_facebook

# --- 1. SIDEBAR MODEL ---
class SidebarWidget(models.Model):
    WIDGET_TYPES = [
        ('AD', 'Google AdSense / Script'),
        ('BANNER', 'Image Banner (Custom)'),
        ('LATEST', 'Latest News List'),
    ]

    title = models.CharField(max_length=100, help_text="पहचान के लिए (e.g. Sidebar Top Ad)")
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, default='LATEST')
    code_content = models.TextField(blank=True, null=True, help_text="AdSense code यहाँ डालें")
    image = models.ImageField(upload_to="sidebar_pics/", blank=True, null=True)
    link = models.URLField(blank=True, null=True, help_text="Banner click link")
    news_limit = models.IntegerField(default=5)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Sidebar Widget"

    def __str__(self):
        return f"{self.title} ({self.widget_type})"


# --- 2. MAIN NEWS MODEL ---
class News(models.Model):
    title = models.CharField(max_length=250)
    status = models.CharField(max_length=20, choices=[('Draft', 'Draft'), ('Published', 'Published')], default='Published')
    category = models.CharField(max_length=100, blank=True, null=True) 
    url_city = models.CharField(max_length=100, blank=True, null=True) 
    district = models.CharField(max_length=100, choices=[(x[0], x[1]) for x in LOCATION_DATA], blank=True, null=True)
    content = RichTextField(blank=True)
    
    # Image logic: Local field for upload, URL field for storage
    image = models.ImageField(upload_to="temp_news/", blank=True, null=True, help_text="AVIF भी सपोर्टेड है, अपलोड अपने आप होगा")
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
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # A. DISTRICT & CATEGORY AUTO-LOGIC
        if self.district:
            d_val = str(self.district).strip()
            found = False
            for item in LOCATION_DATA:
                if len(item) >= 3 and str(item[0]).strip() == d_val:
                    self.category = item[1]
                    self.url_city = slugify(unidecode(item[2]))
                    found = True
                    break
            if not found:
                self.url_city = slugify(unidecode(d_val))
        else:
            self.url_city = 'news'
            if not self.category: self.category = "Uttar Pradesh"

        # B. SLUG LOGIC
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))[:80]}-{str(uuid.uuid4())[:6]}"

        # C. AUTO-UPGRADE IMAGE TO IMGBB (Supports AVIF/WebP)
        if self.image:
            try:
                new_url = process_and_upload_to_imgbb(self)
                if new_url:
                    self.image_url = new_url
                    # सर्वर की मेमोरी बचाने के लिए लोकल पाथ हटा दें
                    self.image = None 
            except Exception as e:
                print(f"Auto Upload Error: {e}")

        # D. SEO KEYWORDS
        if not self.meta_keywords:
            self.meta_keywords = f"{self.title}, {self.district}, {self.category}, Uttar World News"

        super(News, self).save(*args, **kwargs)

        # E. FB AUTO-POSTING (AFTER COMMIT)
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            transaction.on_commit(lambda: self.post_to_fb_handler())

    def post_to_fb_handler(self):
        if post_to_facebook(self):
            News.objects.filter(id=self.id).update(is_fb_posted=True)

    def __str__(self):
        return self.title


# --- 3. ADDITIONAL IMAGES (News के अंदर की फोटोज़) ---
class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="temp_news/")
    image_url = models.URLField(max_length=500, blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.image:
            try:
                new_url = process_and_upload_to_imgbb(self)
                if new_url:
                    self.image_url = new_url
                    self.image = None
            except Exception as e:
                print(f"Extra Image Error: {e}")
        super().save(*args, **kwargs)
