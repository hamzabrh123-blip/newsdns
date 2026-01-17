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
    ]

    DISTRICT_CHOICES = [
        ('Lucknow-UP', 'Lucknow-UP'),
        ('Purvanchal', 'Purvanchal'),
        ('Bahraich-Gonda', 'Bahraich-Gonda'),
        ('Sitapur-Barabanki', 'Sitapur-Barabanki'),
    ]

    title = models.CharField(max_length=250)
    
    # --- यह फ़ील्ड गायब थी, इसे यहाँ वापस जोड़ दिया है ---
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
    )
    # -----------------------------------------------

    district = models.CharField(
        max_length=50,
        choices=DISTRICT_CHOICES,
        blank=True,
        null=True
    )

    date = models.DateTimeField(auto_now_add=True)
    content = RichTextUploadingField(blank=True)
    image = CloudinaryField("Image", blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    is_important = models.BooleanField(default=False)
    slug = models.SlugField(max_length=350, unique=True, blank=True, allow_unicode=True)

    def save(self, *args, **kwargs):
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
