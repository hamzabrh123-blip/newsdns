from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.encoding import force_str
from .utils import upload_to_imgbb 

class News(models.Model):
    CATEGORY_CHOICES = [
        ('International', 'International'),
        ('National', 'National'),
        ('Technology', 'Technology'),
        ('Bollywood', 'Bollywood'),
    ]

    # Location list seedha yahan se manage hogi
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
        help_text="URL के लिए शहर का नाम (जैसे: lucknow). खाली छोड़ने पर District लिया जाएगा।"
    )

    date = models.DateTimeField(auto_now_add=True)
    content = RichTextField(blank=True) # Simple CKEditor for stability
    
    # Upload helper
    image = models.ImageField("Upload Image", upload_to="news_pics/", blank=True, null=True)
    
    # Permanent ImgBB Link
    image_url = models.URLField(max_length=500, blank=True, null=True)
    
    youtube_url = models.URLField(blank=True, null=True)
    is_important = models.BooleanField(default=False)
    slug = models.SlugField(max_length=350, unique=True, blank=True, allow_unicode=True)

    def save(self, *args, **kwargs):
        # 1. Automatic ImgBB Upload
        if self.image:
            try:
                if hasattr(self.image, 'file'):
                    uploaded_link = upload_to_imgbb(self.image)
                    if uploaded_link:
                        self.image_url = uploaded_link
            except Exception as e:
                print(f"ImgBB Error: {e}")

        # 2. URL City Logic
        if not self.url_city:
            if self.district:
                self.url_city = slugify(self.district)
            else:
                self.url_city = "news"
        else:
            self.url_city = slugify(self.url_city)

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
