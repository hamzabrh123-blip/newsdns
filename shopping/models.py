import os
from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from .utils import upload_to_imgbb

# --- 1. HomeSlider ---
class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='temp/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # सीधा मेमोरी से ImgBB पर भेजो और डिस्क सेविंग को रोक दो
        if self.image and hasattr(self.image, 'file'):
            url = upload_to_imgbb(self.image)
            if url:
                self.image_url = url
                self.image = None # फोल्डर में जाने से पहले ही खत्म
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or f"Slider {self.id}"

# --- 2. Category ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='temp/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        if self.image and hasattr(self.image, 'file'):
            url = upload_to_imgbb(self.image)
            if url:
                self.image_url = url
                self.image = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# --- 3. Product ---
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    buy_now_url = models.URLField(max_length=500, blank=True, null=True)
    short_description = models.TextField(max_length=500)
    long_description = RichTextUploadingField() 
    main_image = models.ImageField(upload_to='temp/', null=True, blank=True)
    main_image_url = models.URLField(max_length=500, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title)
        if self.main_image and hasattr(self.main_image, 'file'):
            url = upload_to_imgbb(self.main_image)
            if url:
                self.main_image_url = url
                self.main_image = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- 4. ProductImage (Gallery) ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='temp/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            url = upload_to_imgbb(self.image)
            if url:
                self.image_url = url
                self.image = None
        super().save(*args, **kwargs)
