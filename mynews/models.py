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

# इम्पोर्ट पक्का करें
from .constants import LOCATION_DATA 
from .utils import process_and_upload_to_imgbb, post_to_facebook

# --- 1. SIDEBAR MODEL ---
class SidebarWidget(models.Model):
    WIDGET_TYPES = [
        ('AD', 'Google AdSense / Script'),
        ('BANNER', 'Image Banner (Custom)'),
        ('LATEST', 'Latest News List'),
    ]
    title = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, default='LATEST')
    code_content = models.TextField(blank=True, null=True, help_text="AdSense script यहाँ डालें")
    image = models.FileField(upload_to="sidebar_pics/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    news_limit = models.IntegerField(default=5)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

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
    
    # Image Section
    image = models.FileField(upload_to="temp_news/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    # --- यहाँ फिक्स किया है (Image Caption & ALT Logic) ---
    image_caption = models.CharField(
        max_length=300, 
        blank=True, 
        null=True, 
        help_text="फोटो के नीचे क्या दिखाना है? खाली छोड़ने पर न्यूज़ हेडलाइन ही कैप्शन बनेगी।"
    )
    
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
        # 1. YouTube ID Logic
        if self.youtube_url:
            regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
            match = re.search(regex, self.youtube_url)
            self.youtube_video_id = match.group(1) if match else None

        # 2. SEO & District Logic
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

        # 3. Slug Logic
        if not self.slug:
            slug_base = unidecode(self.title)
            self.slug = f"{slugify(slug_base)[:85]}-{str(uuid.uuid4())[:4]}"

        # 4. AVIF/WebP Auto-Convert (Optimized for 512MB RAM)
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

        # 5. External Services (ImgBB & FB)
        if (self.image and not self.image_url) or (self.share_now_to_fb and not self.is_fb_posted):
            transaction.on_commit(lambda: self.handle_services())

    def handle_services(self):
        updated = False
        if self.image and not self.image_url:
            new_url = process_and_upload_to_imgbb(self)
            if new_url:
                self.image_url = new_url
                self.image = None
                updated = True
        
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
        return self.title


# --- 3. GALLERY / ADDITIONAL IMAGES ---
class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='additional_images', on_delete=models.CASCADE)
    image = models.FileField(upload_to="temp_news/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
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
        
        if self.image and not self.image_url:
            transaction.on_commit(lambda: self.upload_gallery_image())

    def upload_gallery_image(self):
        try:
            new_url = process_and_upload_to_imgbb(self)
            if new_url:
                NewsImage.objects.filter(id=self.id).update(image_url=new_url, image=None)
        except Exception as e:
            print(f"Gallery Upload Error: {e}")
