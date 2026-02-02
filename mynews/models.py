import uuid
from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.encoding import force_str
from django.utils.timezone import now
from unidecode import unidecode
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
        help_text="URL ke liye shehar ka naam. Khali chhodne par District liya jayega."
    )

    date = models.DateTimeField(default=now) # auto_now_add se hata kar default kiya
    content = RichTextField(blank=True) 
    
    image = models.ImageField("Upload Image", upload_to="news_pics/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    youtube_url = models.URLField(blank=True, null=True)
    is_important = models.BooleanField(default=False)
    
    # SEO & Slug
    meta_keywords = models.CharField(max_length=500, blank=True, null=True, help_text="Keywords comma se alag karein")
    slug = models.SlugField(max_length=500, unique=True, blank=True)

    # FB status check
    is_fb_posted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # 1. ImgBB Upload Logic
        if self.image:
            try:
                uploaded_link = upload_to_imgbb(self.image)
                if uploaded_link:
                    self.image_url = uploaded_link
                    self.image = None 
            except Exception as e:
                print(f"ImgBB Error: {e}")

        # 2. URL City Logic (City slugify)
        if not self.url_city:
            self.url_city = slugify(unidecode(self.district)) if self.district else "news"
        else:
            self.url_city = slugify(unidecode(self.url_city))

        # 3. Aaj Tak Style Slug (English + ID + Date)
        if not self.slug:
            # Hindi title ko English jaisa convert karo
            roman_title = unidecode(self.title)
            base_slug = slugify(roman_title)
            
            # Unique ID + Current Date
            unique_id = str(uuid.uuid4())[:8]
            date_str = now().strftime('%Y-%m-%d')
            
            self.slug = f"{base_slug}-{unique_id}-{date_str}"

        # Pehle news ko save karo taaki FB ko data sahi mile
        super().save(*args, **kwargs)

        # 4. FACEBOOK AUTOMATIC POSTING
        if not self.is_fb_posted:
            try:
                # Local import taaki view aur model ke bich circular import ka chakkar na ho
                from .views import post_to_facebook_network # dhyaan do ki tumhari view file ka sahi path ho
                
                # FB function call
                post_to_facebook_network(self)
                
                # Status update bina save() dubara trigger kiye
                News.objects.filter(id=self.id).update(is_fb_posted=True)
            except Exception as fb_err:
                print(f"Facebook Posting System Error: {fb_err}")

    def __str__(self):
        return self.title
