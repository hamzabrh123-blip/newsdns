from django.db import models
# CloudinaryField hata diya hai
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.utils.encoding import force_str
from .utils import upload_to_imgbb 

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class News(models.Model):
    CATEGORY_CHOICES = [
        ('International', 'International'),
        ('National', 'National'),
        ('Technology', 'Technology'),
        ('Bollywood', 'Bollywood'),
    ]

    DISTRICT_CHOICES = [
        ('Lucknow-UP', 'Lucknow-UP'),
        ('UP-National', 'UP-National'),
        ('Purvanchal', 'Purvanchal'),
        ('Bahraich-Gonda', 'Bahraich-Gonda'),
        ('Balrampur-Shravasti', 'Balrampur-Shravasti'),
        ('Sitapur-Barabanki', 'Sitapur-Barabanki'),
    ]

    title = models.CharField(max_length=250)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True, null=True)
    district = models.CharField(max_length=50, choices=DISTRICT_CHOICES, blank=True, null=True)
    
    url_city = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="URL के लिए शहर का नाम (जैसे: New York). खाली छोड़ने पर District का नाम लिया जाएगा।"
    )

    date = models.DateTimeField(auto_now_add=True)
    content = RichTextUploadingField(blank=True)
    
    # CloudinaryField ki jagah normal ImageField (Taki API Key ka error na aaye)
    image = models.ImageField("Image", upload_to="news_pics/", blank=True, null=True)
    
    # Nayi photos ka ImgBB link yahan save hoga
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    youtube_url = models.URLField(blank=True, null=True)
    is_important = models.BooleanField(default=False)
    slug = models.SlugField(max_length=350, unique=True, blank=True, allow_unicode=True)

    def save(self, *args, **kwargs):
        # 1. ImgBB Logic
        if self.image and not self.image_url:
            try:
                # Sirf nayi upload ki gayi files ke liye (InMemoryUploadedFile)
                if hasattr(self.image, 'file'):
                    uploaded_link = upload_to_imgbb(self.image)
                    if uploaded_link:
                        self.image_url = uploaded_link
            except Exception as e:
                print(f"Error uploading to ImgBB: {e}")

        # 2. City URL Logic
        if self.url_city:
            self.url_city = slugify(self.url_city)
        elif self.district:
            self.url_city = slugify(self.district)
        else:
            self.url_city = "news"

        # 3. Slug Logic
        if not self.slug:
            base_slug = slugify(force_str(self.title), allow_unicode=True)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title