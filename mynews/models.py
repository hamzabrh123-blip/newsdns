import uuid
import re
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from .constants import LOCATION_DATA 
from .utils import process_and_upload_to_imgbb, post_to_facebook

# --- 1. SIDEBAR MODEL (Admin se Ads/Banner handle karne ke liye) ---
class SidebarWidget(models.Model):
    WIDGET_TYPES = [
        ('AD', 'Google AdSense / Script'),
        ('BANNER', 'Image Banner (Custom)'),
        ('LATEST', 'Latest News List'),
    ]

    title = models.CharField(max_length=100, help_text="Pehchan ke liye (e.g. Sidebar Top Ad)")
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, default='LATEST')
    code_content = models.TextField(blank=True, null=True, help_text="AdSense code ya HTML yahan dale")
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
        # A. DISTRICT & CATEGORY LOGIC
        if self.district:
            d_val = str(self.district).strip()
            found_in_data = False
            for item in LOCATION_DATA:
                try:
                    if len(item) >= 3 and str(item[0]).strip() == d_val:
                        self.category = item[1]  
                        self.url_city = slugify(unidecode(item[2])) 
                        found_in_data = True
                        break
                except: continue
            if not found_in_data:
                self.url_city = slugify(unidecode(d_val))
        else:
            self.url_city = 'news'
            if not self.category: self.category = "Uttar Pradesh"

        # B. SLUG LOGIC
        if not self.slug:
            base_slug = slugify(unidecode(self.title))[:60]
            self.slug = f"{base_slug}-{str(uuid.uuid4())[:6]}"

        # C. MAIN IMAGE IMGBB UPLOAD
        if self.image and not self.image_url:
            try:
                link = process_and_upload_to_imgbb(self)
                if link: self.image_url = link
            except Exception as e: print(f"Main Image Upload Error: {e}")

        super(News, self).save(*args, **kwargs)

        # D. FACEBOOK AUTO-POST
        try:
            if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
                if self.image_url:
                    if post_to_facebook(self):
                        News.objects.filter(id=self.id).update(is_fb_posted=True)
        except Exception as e: print(f"FB Posting Error: {e}")

    def __str__(self):
        return f"{self.title} | ({self.district})"


# --- 3. MULTI-IMAGE MODEL (News ke beech/neeche ke liye) ---
class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="news_pics/")
    image_url = models.URLField(max_length=500, blank=True, null=True) # Extra images bhi ImgBB par jayengi
    caption = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Additional images ko bhi ImgBB par bhejne ka logic
        if self.image and not self.image_url:
            try:
                # process_and_upload_to_imgbb ko self pass kar rahe hain
                link = process_and_upload_to_imgbb(self) 
                if link: self.image_url = link
            except Exception as e: print(f"Extra Image Upload Error: {e}")
        super().save(*args, **kwargs)
