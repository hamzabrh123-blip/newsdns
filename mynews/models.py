import uuid
import os
import re
import io
from django.db import models, transaction
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from ckeditor.fields import RichTextField
from PIL import Image
from django.core.files.base import ContentFile

# अपनी फाइल्स से इम्पोर्ट पक्का करें
from .constants import LOCATION_DATA 
from .utils import process_and_upload_to_imgbb, post_to_facebook

# --- 1. SIDEBAR MODEL (AdSense के लिए) ---
class SidebarWidget(models.Model):
    WIDGET_TYPES = [
        ('AD', 'Google AdSense / Script'),
        ('BANNER', 'Image Banner (Custom)'),
        ('LATEST', 'Latest News List'),
    ]
    title = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, default='LATEST')
    code_content = models.TextField(blank=True, null=True, help_text="AdSense script यहाँ डालें")
    image = models.FileField(upload_to="sidebar_pics/", blank=True, null=True) # FileField for AVIF/WebP
    link = models.URLField(blank=True, null=True)
    news_limit = models.IntegerField(default=5)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.widget_type})"


# --- 2. MAIN NEWS MODEL (Bulletproof Version) ---
class News(models.Model):
    title = models.CharField(max_length=250)
    status = models.CharField(max_length=20, choices=[('Draft', 'Draft'), ('Published', 'Published')], default='Published')
    category = models.CharField(max_length=100, blank=True, null=True) 
    url_city = models.CharField(max_length=100, blank=True, null=True) 
    district = models.CharField(max_length=100, choices=[(x[0], x[1]) for x in LOCATION_DATA], blank=True, null=True)
    content = RichTextField(blank=True)
    
    # AVIF/WebP के लिए FileField ज़रूरी है
    image = models.FileField(upload_to="temp_news/", blank=True, null=True)
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
        # A. YouTube Logic
        if self.youtube_url:
            regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
            match = re.search(regex, self.youtube_url)
            self.youtube_video_id = match.group(1) if match else None

        # B. District & Category Logic
        if self.district:
            d_val = str(self.district).strip()
            for item in LOCATION_DATA:
                if len(item) >= 3 and str(item[0]).strip() == d_val:
                    self.category = item[1]
                    self.url_city = slugify(unidecode(item[2])).lower()
                    break
        else:
            if not self.url_city: self.url_city = 'news'
            if not self.category: self.category = "Uttar Pradesh"

        # C. SEO Friendly Slug
        if not self.slug:
            slug_base = unidecode(self.title)
            self.slug = f"{slugify(slug_base)[:85]}-{str(uuid.uuid4())[:4]}"

        # D. AVIF/WebP Auto-Convert (Admin Panel Error Fix)
        if self.image and not self.image_url:
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                output = io.BytesIO()
                img.save(output, format='WEBP', quality=75)
                output.seek(0)
                new_name = f"{os.path.splitext(self.image.name)[0]}.webp"
                self.image.save(new_name, ContentFile(output.read()), save=False)
            except:
                pass

        super(News, self).save(*args, **kwargs)

        # E. External Services (Post-Save)
        if (self.image and not self.image_url) or (self.share_now_to_fb and not self.is_fb_posted):
            transaction.on_commit(lambda: self.handle_services())

    def handle_services(self):
        updated = False
        # ImgBB Upload logic
        if self.image and not self.image_url:
            new_url = process_and_upload_to_imgbb(self)
            if new_url:
                self.image_url = new_url
                self.image = None
                updated = True
        
        # Facebook Sharing with Full Image URL
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            if post_to_facebook(self):
                self.is_fb_posted = True
                updated = True
        
        if updated:
            News.objects.filter(id=self.id).update(
                image_url=self.image_url, 
                image=self.image, 
                is_fb_posted=self.is_fb_posted
            )

    def __str__(self):
        return self.title or "Untitled News"


# --- 3. GALLERY / ADDITIONAL IMAGES (Multiple Upload Support) ---
class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='additional_images', on_delete=models.CASCADE)
    image = models.FileField(upload_to="temp_news/", blank=True, null=True) # AVIF/WebP Support
    image_url = models.URLField(max_length=500, blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Gallery Image Optimization
        if self.image and not self.image_url:
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                output = io.BytesIO()
                img.save(output, format='WEBP', quality=75)
                output.seek(0)
                new_name = f"gallery_{uuid.uuid4().hex[:8]}.webp"
                self.image.save(new_name, ContentFile(output.read()), save=False)
            except:
                pass

        super().save(*args, **kwargs)
        
        # Gallery Upload to ImgBB
        if self.image and not self.image_url:
            transaction.on_commit(lambda: self.upload_gallery_image())

    def upload_gallery_image(self):
        try:
            # NewsImage के लिए अलग से upload logic या same function
            new_url = process_and_upload_to_imgbb(self)
            if new_url:
                NewsImage.objects.filter(id=self.id).update(image_url=new_url, image=None)
        except Exception as e:
            print(f"Gallery Upload Error: {e}")

    def __str__(self):
        return f"Gallery Image for {self.news.title[:30]}"
