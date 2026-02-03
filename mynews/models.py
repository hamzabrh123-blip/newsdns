import uuid
import facebook
from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from django.urls import reverse
from django.conf import settings
from .utils import upload_to_imgbb 

class News(models.Model):
    # MASTER CONTROLLER: Inhi se poori site chalegi
    LOCATION_CHOICES = [
        # --- International ---
        ('Int-MiddleEast', 'मिडिल ईस्ट (Middle East)'),
        ('Int-America', 'अमेरिका (America-Canada)'),
        ('International', 'अंतर्राष्ट्रीय (International)'),
        
        # --- Sports & Entertainment ---
        ('Sports', 'खेल जगत (Sports)'),
        ('Bollywood', 'बॉलीवुड (Bollywood)'),
        ('Hollywood', 'हॉलीवुड (Hollywood)'),

        # --- Tech & Business ---
        ('Technology', 'टेक्नोलॉजी (Tech)'),
        ('Market', 'मार्केट / बिज़नेस (Market)'),

        # --- Uttar Pradesh & Others ---
        ('Lucknow-UP', 'लखनऊ न्यूज़'),
        ('UP-National', 'यूपी राष्ट्रीय'),
        ('Purvanchal', 'पूर्वांचल'),
        ('Bahraich-Gonda', 'बहराइच-गोण्डा'),
        ('Balrampur-Shravasti', 'बलरामपुर-श्रावस्ती'),
        ('Sitapur-Barabanki', 'सीतापुर-बाराबंकी'),
        ('Other-States', 'अन्य राज्य (Other States)'),
    ]

    title = models.CharField(max_length=250)
    category = models.CharField(max_length=100, blank=True, null=True) # General tag ke liye
    district = models.CharField(max_length=50, choices=LOCATION_CHOICES, blank=True, null=True)
    
    url_city = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Khali chhodne par 'news' ya district name liya jayega."
    )

    date = models.DateTimeField(default=now)
    content = RichTextField(blank=True) 
    
    image = models.ImageField("Upload Image", upload_to="news_pics/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    youtube_url = models.URLField(blank=True, null=True)
    is_important = models.BooleanField(default=False, verbose_name="Breaking News?")
    
    meta_keywords = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=500, unique=True, blank=True)

    share_now_to_fb = models.BooleanField(default=False, verbose_name="Facebook par abhi bhejein?")
    is_fb_posted = models.BooleanField(default=False, verbose_name="FB par post ho chuka hai")

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'url_city': self.url_city, 'slug': self.slug})

    def save(self, *args, **kwargs):
        # 1. Image Upload Logic
        if self.image:
            try:
                uploaded_link = upload_to_imgbb(self.image)
                if uploaded_link:
                    self.image_url = uploaded_link
                    self.image = None 
            except Exception as e:
                print(f"ImgBB Error: {e}")

        # 2. City Logic (Isi se district_news.html track hota hai)
        if not self.url_city:
            self.url_city = slugify(unidecode(self.district)) if self.district else "news"
        else:
            self.url_city = slugify(unidecode(self.url_city))

        # 3. Slug Generation
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))}-{str(uuid.uuid4())[:8]}-{now().strftime('%Y-%m-%d')}"

        super().save(*args, **kwargs)

        # 4. Facebook Posting Logic
        if self.share_now_to_fb and not self.is_fb_posted:
            try:
                token = settings.FB_ACCESS_TOKEN
                page_id = settings.FB_PAGE_ID
                graph = facebook.GraphAPI(access_token=token)
                site_domain = "https://uttarworld.com"
                full_news_url = f"{site_domain}{self.get_absolute_url()}"
                final_img = self.image_url if self.image_url else ""
                message = f"🔥 {self.title}\n\nPuri khabar padhein: {full_news_url}"

                graph.put_object(
                    parent_object=page_id,
                    connection_name='feed',
                    message=message,
                    link=full_news_url,
                    picture=final_img
                )
                News.objects.filter(id=self.id).update(is_fb_posted=True, share_now_to_fb=False)
            except Exception as fb_err:
                print(f"❌ FB Error: {fb_err}")

    def __str__(self):
        return self.title
