from django.db import models
from cloudinary.models import CloudinaryField
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from django.utils.encoding import force_str

# 1. District Model: यहाँ से आप Admin Panel में जिले जोड़ेंगे
class District(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# 2. News Model: मुख्य न्यूज़ टेबल
class News(models.Model):

    CATEGORY_CHOICES = [
        ('International', 'International'),
        ('National', 'National'),
    ]

    title = models.CharField(max_length=250)

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
    )

    # हमने ForeignKey का इस्तेमाल किया है ताकि आप Admin से नए जिले जोड़ सकें
   district = models.CharField(
    max_length=50,
    choices=DISTRICT_CHOICES,
    blank=True,
    null=True
)

    date = models.DateTimeField(auto_now_add=True)

    # CKEditor के लिए फील्ड
    content = RichTextUploadingField(blank=True)

    # Cloudinary के लिए मुख्य इमेज
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
        blank=True,
        allow_unicode=True   # ✅ हिंदी स्लग सपोर्ट के लिए
    )

    # ✅ AUTO SAFE SLUG (Hindi + English + Duplicate Safe)
    def save(self, *args, **kwargs):
        if not self.slug:
            # force_str हिंदी शब्दों को सही से स्लग में बदलता है
            base_slug = slugify(force_str(self.title), allow_unicode=True)
            slug = base_slug
            counter = 1

            # अगर स्लग पहले से मौजूद है, तो उसके आगे नंबर जोड़ देगा (जैसे: taza-khabar-1)
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# 3. Comment Model: न्यूज़ पर कमेंट्स के लिए
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

    # कमेंट को अप्रूव करने का सिस्टम (बाद के लिए अच्छा है)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} on {self.news.title}"
