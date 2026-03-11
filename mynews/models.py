import uuid
import os
import re
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
    title = models.CharField(max_length=100, help_text="पहचान के लिए")
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, default='LATEST')
    code_content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="sidebar_pics/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
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
    image = models.ImageField(upload_to="temp_news/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    youtube_url = models.URLField(blank=True, null=True)
    youtube_video_id = models.CharField(max_length=20, blank=True, null=True, editable=False)

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
        if self.youtube_url:
            regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
            match = re.search(regex, self.youtube_url)
            self.youtube_video_id = match.group(1) if match else None

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

        if not self.slug:
            slug_base = unidecode(self.title)
            if not slug_base.strip(): slug_base = "news-article"
            self.slug = f"{slugify(slug_base)[:80]}-{str(uuid.uuid4())[:6]}"

        is_new_image = True if self.image and not self.image_url else False

        super(News, self).save(*args, **kwargs)

        if is_new_image:
            try:
                new_url = process_and_upload_to_imgbb(self)
                if new_url:
                    News.objects.filter(id=self.id).update(image_url=new_url, image=None)
            except Exception as e:
                print(f"Auto Upload Error: {e}")

        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            try:
                transaction.on_commit(lambda: self.post_to_fb_handler())
            except:
                pass

    def post_to_fb_handler(self):
        if post_to_facebook(self):
            News.objects.filter(id=self.id).update(is_fb_posted=True)

    def __str__(self):
        return self.title or "Untitled News"


# --- 3. ADDITIONAL IMAGES (FIXED) ---
class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="temp_news/", blank=True, null=True) # Changed to Null/Blank
    image_url = models.URLField(max_length=500, blank=True, null=True) # Null/Blank for DB
    caption = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new_img = True if self.image and not self.image_url else False
        super().save(*args, **kwargs)
        
        if is_new_img:
            try:
                new_url = process_and_upload_to_imgbb(self)
                if new_url:
                    NewsImage.objects.filter(id=self.id).update(image_url=new_url, image=None)
            except Exception as e:
                print(f"Additional Image Error: {e}")

    def __str__(self):
        return f"Image for {self.news.title[:30]}..."
