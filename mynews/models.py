from django.db import models
from cloudinary.models import CloudinaryField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify


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
        ('Lucknow', 'Lucknow'),
        ('Bahraich', 'Bahraich'),
        ('Gonda', 'Gonda'),
        ('Shravasti-Balrampur', 'Shravasti-Balrampur'),
        ('Sitapur-Barabanki', 'Sitapur-Barabanki'),
    ]

    title = models.CharField(max_length=250)

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
    )

    district = models.CharField(
        max_length=50,
        choices=DISTRICT_CHOICES,
        blank=True,
        null=True
    )

    date = models.DateTimeField(auto_now_add=True)

    content = RichTextUploadingField(blank=True)

    image = CloudinaryField(
        "Image",
        blank=True,
        null=True
    )

    youtube_url = models.URLField(blank=True, null=True)

    is_important = models.BooleanField(default=False)

    slug = models.SlugField(
        max_length=350,
        unique=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)   # ✅ FIXED
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} on {self.news.title}"


class AdminOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"
