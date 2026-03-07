import uuid
import os
from django.db import models, transaction
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from ckeditor.fields import RichTextField
from .constants import LOCATION_DATA 
from .utils import process_and_upload_to_imgbb, post_to_facebook

# --- 2. MAIN NEWS MODEL ---
class News(models.Model):
    # ... (fields remain same) ...
    title = models.CharField(max_length=250)
    status = models.CharField(max_length=20, choices=[('Draft', 'Draft'), ('Published', 'Published')], default='Published')
    category = models.CharField(max_length=100, blank=True, null=True) 
    url_city = models.CharField(max_length=100, blank=True, null=True) 
    district = models.CharField(max_length=100, choices=[(x[0], x[1]) for x in LOCATION_DATA], blank=True, null=True)
    content = RichTextField(blank=True)
    image = models.ImageField(upload_to="temp_news/", blank=True, null=True)
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
        # A. DISTRICT & CATEGORY
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

        # B. SLUG LOGIC (Improved for Hindi)
        if not self.slug:
            slug_base = unidecode(self.title)
            if not slug_base.strip(): # अगर टाइटल शुद्ध हिंदी है और unidecode फेल हो जाए
                slug_base = "news-article"
            self.slug = f"{slugify(slug_base)[:80]}-{str(uuid.uuid4())[:6]}"

        # C. IMAGE UPLOAD logic
        # पहले super() save करें ताकि ID मिल जाए, फिर इमेज अपलोड करें
        is_new_image = False
        if self.image and not self.image_url:
            is_new_image = True

        super(News, self).save(*args, **kwargs)

        if is_new_image:
            try:
                new_url = process_and_upload_to_imgbb(self)
                if new_url:
                    # Update without calling save() again to avoid recursion
                    News.objects.filter(id=self.id).update(image_url=new_url, image=None)
            except Exception as e:
                print(f"Auto Upload Error: {e}")

        # D. FB POSTING
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            try:
                transaction.on_commit(lambda: self.post_to_fb_handler())
            except:
                pass # Prevent 500 if transaction fails

    def post_to_fb_handler(self):
        if post_to_facebook(self):
            News.objects.filter(id=self.id).update(is_fb_posted=True)

    def __str__(self):
        return self.title or "Untitled News"
