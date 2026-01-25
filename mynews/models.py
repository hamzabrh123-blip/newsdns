from django.db import models
from cloudinary.models import CloudinaryField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.utils.encoding import force_str

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

    # आपके पुराने डिस्ट्रिक्ट पेज के लिए चॉइस (इसे टच नहीं किया गया)
    DISTRICT_CHOICES = [
        ('Lucknow-UP', 'Lucknow-UP'),
        ('UP-National', 'UP-National'),
        ('Purvanchal', 'Purvanchal'),
        ('Bahraich-Gonda', 'Bahraich-Gonda'),
        ('Balrampur-Shravasti', 'Balrampur-Shravasti'),
        ('Sitapur-Barabanki', 'Sitapur-Barabanki'),
    ]

    title = models.CharField(max_length=250)
    
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
    )

    # पुराने पेज को चलाने के लिए डिस्ट्रिक्ट चॉइस
    district = models.CharField(
        max_length=50,
        choices=DISTRICT_CHOICES,
        blank=True,
        null=True
    )

    # ✅ नया फ़ील्ड: URL में शहर का नाम दिखाने के लिए (जैसे: New_York)
    # अगर इसे खाली छोड़ेंगे तो district का नाम अपने आप यहाँ आ जाएगा
    url_city = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="URL के लिए शहर का नाम (जैसे: New York). खाली छोड़ने पर District का नाम लिया जाएगा।"
    )

    date = models.DateTimeField(auto_now_add=True)
    content = RichTextUploadingField(blank=True)
    image = CloudinaryField("Image", blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    is_important = models.BooleanField(default=False)
    slug = models.SlugField(max_length=350, unique=True, blank=True, allow_unicode=True)

    def save(self, *args, **kwargs):
        # 1. URL के लिए शहर का नाम तैयार करना
        if not self.url_city:
            if self.district:
                # 'Lucknow-UP' को 'lucknow-up' बनाएगा
                self.url_city = self.district.lower()
            else:
                self.url_city = "news"
        
        # स्पेस को हटाकर underscore (_) लगाना (e.g. 'New York' -> 'new_york')
        self.url_city = self.url_city.strip().replace(" ", "_").lower()

        # 2. स्लग बनाना
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

class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} on {self.news.title}"
