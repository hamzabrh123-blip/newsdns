import uuid
import os
import re
from django.db import models, transaction
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.safestring import mark_safe
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
    image = models.ImageField(upload_to="temp_news/", blank=True, null=True) # Image 1
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

    # --- जादुई लॉजिक: कंटेंट के बीच में इमेज सेट करना ---
    @property
    def processed_content(self):
        text = self.content
        
        # 1. मेन इमेज (Image 1) के लिए {img1}
        if "{img1}" in text and self.image_url:
            main_tag = f'''
            <div class="post-img main-img" style="margin:20px 0; text-align:center;">
                <img src="{self.image_url}" class="img-fluid" style="border-radius:8px; max-width:100%;">
            </div>'''
            text = text.replace("{img1}", main_tag)

        # 2. गैलरी इमेजेस (Image 2, 3...) के लिए {lib1}, {lib2}
        # यहाँ 'additional_images' वो नाम है जो नीचे ForeignKey में related_name है
        gallery = self.additional_images.all().order_by('id')
        for i, g_img in enumerate(gallery, 1):
            placeholder = f"{{lib{i}}}"
            if placeholder in text:
                url = g_img.image_url if g_img.image_url else (g_img.image.url if g_img.image else "")
                if url:
                    lib_tag = f'''
                    <div class="post-img lib-img" style="margin:20px 0; text-align:center;">
                        <img src="{url}" class="img-fluid" style="border-radius:8px; max-width:100%;">
                        {f'<p style="color:#666; font-size:14px; margin-top:5px;">{g_img.caption}</p>' if g_img.caption else ''}
                    </div>'''
                    text = text.replace(placeholder, lib_tag)
        
        return mark_safe(text)

    def save(self, *args, **kwargs):
        # 1. YouTube ID Logic
        if self.youtube_url:
            regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
            match = re.search(regex, self.youtube_url)
            self.youtube_video_id = match.group(1) if match else None

        # 2. Location Logic
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

        # 3. Slug Logic
        if not self.slug:
            slug_base = unidecode(self.title)
            if not slug_base.strip(): slug_base = "news-article"
            self.slug = f"{slugify(slug_base)[:80]}-{str(uuid.uuid4())[:6]}"

        # 4. Check for image
        is_new_image = True if self.image and not self.image_url else False

        # 5. Database Commit
        super(News, self).save(*args, **kwargs)

        # 6. ImgBB Upload (Logo and Process logic inside utils)
        if is_new_image:
            transaction.on_commit(lambda: self.handle_main_image_upload())

        # 7. FB Posting
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            transaction.on_commit(lambda: self.post_to_fb_handler())

    def handle_main_image_upload(self):
        try:
            # यह वही फंक्शन है जो आपने utils.py में अपडेट किया है
            new_url = process_and_upload_to_imgbb(self)
            if new_url:
                News.objects.filter(id=self.id).update(image_url=new_url, image=None)
        except Exception as e:
            print(f"Auto Upload Error: {e}")

    def post_to_fb_handler(self):
        if post_to_facebook(self):
            News.objects.filter(id=self.id).update(is_fb_posted=True)

    def __str__(self):
        return self.title or "Untitled News"


# --- 3. ADDITIONAL IMAGES (LIBRARY/GALLERY) ---
class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="temp_news/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new_img = True if self.image and not self.image_url else False
        
        # 1. Save Record
        super().save(*args, **kwargs)
        
        # 2. Upload with Logo processing
        if is_new_img:
            transaction.on_commit(lambda: self.handle_gallery_upload())

    def handle_gallery_upload(self):
        try:
            # यह भी वही यूनिवर्सल फंक्शन इस्तेमाल करेगा
            new_url = process_and_upload_to_imgbb(self)
            if new_url:
                NewsImage.objects.filter(id=self.id).update(image_url=new_url, image=None)
        except Exception as e:
            print(f"Gallery Image Error: {e}")

    def __str__(self):
        return f"Image for {self.news.title[:30]}..."