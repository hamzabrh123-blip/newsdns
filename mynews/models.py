import uuid
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from django.urls import reverse
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

    def get_absolute_url(self):
        city = self.url_city if self.url_city else "news"
        return reverse('news_detail', kwargs={'url_city': city, 'slug': self.slug})

    def save(self, *args, **kwargs):
        # 1. ऑटोमेटिक जिला और स्लग सेट करना
        if self.district:
            for eng, hin, city_slug in LOCATION_DATA:
                if self.district == eng:
                    self.url_city = eng.lower()
                    self.category = hin
                    break
        
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))[:60]}-{str(uuid.uuid4())[:6]}"

        # 2. पहले बेसिक डेटा सेव करें
        super(News, self).save(*args, **kwargs)

        # 3. इमेज प्रोसेसिंग (Watermark + ImgBB) - सिर्फ तब जब URL न हो
        if self.image and not self.image_url:
            uploaded_link = process_and_upload_to_imgbb(self)
            if uploaded_link:
                # सीधे DB अपडेट करें ताकि दोबारा save() कॉल न हो (Recursion से बचाव)
                News.objects.filter(id=self.id).update(image_url=uploaded_link)

        # 4. फेसबुक ऑटो-पोस्ट (Published न्यूज़ के लिए)
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            if post_to_facebook(self):
                News.objects.filter(id=self.id).update(is_fb_posted=True)

    def __str__(self):
        return self.title
