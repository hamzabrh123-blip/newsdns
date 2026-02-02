import uuid
from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from django.urls import reverse
from .utils import upload_to_imgbb 

class News(models.Model):
    CATEGORY_CHOICES = [
        ('International', 'International'),
        ('National', 'National'),
        ('Technology', 'Technology'),
        ('Bollywood', 'Bollywood'),
        ('Market', 'Market'),
    ]

    LOCATION_CHOICES = [
        ('Lucknow-UP', 'Lucknow-UP'),
        ('UP-National', 'UP-National'),
        ('Purvanchal', 'Purvanchal'),
        ('Bahraich-Gonda', 'Bahraich-Gonda'),
        ('Balrampur-Shravasti', 'Balrampur-Shravasti'),
        ('Sitapur-Barabanki', 'Sitapur-Barabanki'),
    ]

    title = models.CharField(max_length=250)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True, null=True)
    district = models.CharField(max_length=50, choices=LOCATION_CHOICES, blank=True, null=True)
    
    url_city = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Khali chhodne par 'news' liya jayega."
    )

    date = models.DateTimeField(default=now)
    content = RichTextField(blank=True) 
    
    image = models.ImageField("Upload Image", upload_to="news_pics/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    youtube_url = models.URLField(blank=True, null=True)
    is_important = models.BooleanField(default=False, verbose_name="Breaking News?")
    
    meta_keywords = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=500, unique=True, blank=True)

    # FB CONTROLS
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Facebook par abhi bhejein?")
    is_fb_posted = models.BooleanField(default=False, verbose_name="FB par post ho chuka hai")

    def get_absolute_url(self):
        """Asli magic: Ye hamesha working link generate karega"""
        return reverse('news_detail', kwargs={'url_city': self.url_city, 'slug': self.slug})

    def save(self, *args, **kwargs):
        # 1. Image Upload
        if self.image:
            try:
                uploaded_link = upload_to_imgbb(self.image)
                if uploaded_link:
                    self.image_url = uploaded_link
                    self.image = None 
            except Exception as e:
                print(f"ImgBB Error: {e}")

        # 2. City Logic Fix (No more 404)
        if not self.url_city:
            if self.district:
                self.url_city = slugify(unidecode(self.district))
            else:
                self.url_city = "news"
        else:
            self.url_city = slugify(unidecode(self.url_city))

        # 3. Slug Generation
        if not self.slug:
            roman_title = unidecode(self.title)
            base_slug = slugify(roman_title)
            unique_id = str(uuid.uuid4())[:8]
            date_str = now().strftime('%Y-%m-%d')
            self.slug = f"{base_slug}-{unique_id}-{date_str}"

        super().save(*args, **kwargs)

        # 4. FB Auto-Trigger
        if self.share_now_to_fb and not self.is_fb_posted:
            try:
                from .views import post_to_facebook_network
                success = post_to_facebook_network(self)
                if success:
                    News.objects.filter(id=self.id).update(is_fb_posted=True, share_now_to_fb=False)
            except Exception as fb_err:
                print(f"FB System Error: {fb_err}")

    def __str__(self):
        return self.title