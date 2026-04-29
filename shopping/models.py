import uuid
from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from unidecode import unidecode
from .utils import process_and_upload_to_imgbb  # तेरा न्यूज़ वाला सटीक फंक्शन

# --- 1. HomeSlider ---
class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_new_img = bool(self.image and not self.image_url)
        super().save(*args, **kwargs)
        if is_new_img:
            self.handle_upload()

    def handle_upload(self):
        try:
            new_url = process_and_upload_to_imgbb(self)
            if new_url:
                HomeSlider.objects.filter(id=self.id).update(image_url=new_url, image=None)
        except Exception as e:
            print(f"Slider Error: {e}")

# --- 2. Category ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(unidecode(self.name))
        is_new_img = bool(self.image and not self.image_url)
        super().save(*args, **kwargs)
        if is_new_img:
            self.handle_upload()

    def handle_upload(self):
        try:
            new_url = process_and_upload_to_imgbb(self)
            if new_url:
                Category.objects.filter(id=self.id).update(image_url=new_url, image=None)
        except Exception as e:
            print(f"Category Error: {e}")

# --- 3. Product ---
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    buy_now_url = models.URLField(max_length=500, blank=True, null=True)
    short_description = models.TextField(max_length=500)
    long_description = RichTextUploadingField() 
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))[:80]}-{str(uuid.uuid4())[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- 4. ProductImage (Gallery) ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        is_new_img = bool(self.image and not self.image_url)
        super().save(*args, **kwargs)
        if is_new_img:
            self.handle_gallery_upload()

    def handle_gallery_upload(self):
        try:
            new_url = process_and_upload_to_imgbb(self)
            if new_url:
                # Direct Database Update
                ProductImage.objects.filter(id=self.id).update(image_url=new_url, image=None)
        except Exception as e:
            print(f"Gallery Error: {e}")
