import os
import uuid
from django.db import models, transaction
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from .utils import upload_to_imgbb

# --- HELPER: फिजिकल फाइल डिलीट करने के लिए ---
def cleanup_local_file(instance, field_name):
    try:
        file_field = getattr(instance, field_name)
        if file_field and hasattr(file_field, 'path') and os.path.exists(file_field.path):
            os.remove(file_field.path)
            print(f"✅ Local file deleted: {file_field.path}")
    except Exception as e:
        print(f"⚠️ Cleanup Error: {e}")

# --- 1. HomeSlider ---
class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='sliders/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_new_upload = False
        if self.image:
            if not self.pk:
                is_new_upload = True
            else:
                old_obj = HomeSlider.objects.filter(pk=self.pk).first()
                if old_obj and old_obj.image != self.image:
                    is_new_upload = True

        super().save(*args, **kwargs)

        if is_new_upload:
            # save के बाद तुरंत अपलोड और क्लीनअप
            url = upload_to_imgbb(self.image)
            if url:
                cleanup_local_file(self, 'image')
                HomeSlider.objects.filter(pk=self.pk).update(image_url=url, image=None)

    def __str__(self):
        return self.title or f"Slider {self.id}"

# --- 2. Category ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        is_new_upload = False
        if self.image:
            if not self.pk:
                is_new_upload = True
            else:
                old_obj = Category.objects.filter(pk=self.pk).first()
                if old_obj and old_obj.image != self.image:
                    is_new_upload = True

        super().save(*args, **kwargs)

        if is_new_upload:
            url = upload_to_imgbb(self.image)
            if url:
                cleanup_local_file(self, 'image')
                Category.objects.filter(pk=self.pk).update(image_url=url, image=None)

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
    main_image = models.ImageField(upload_to='products/main/', null=True, blank=True)
    main_image_url = models.URLField(max_length=500, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title)
        is_new_upload = False
        if self.main_image:
            if not self.pk:
                is_new_upload = True
            else:
                old_obj = Product.objects.filter(pk=self.pk).first()
                if old_obj and old_obj.main_image != self.main_image:
                    is_new_upload = True

        super().save(*args, **kwargs)

        if is_new_upload:
            url = upload_to_imgbb(self.main_image)
            if url:
                cleanup_local_file(self, 'main_image')
                Product.objects.filter(pk=self.pk).update(main_image_url=url, main_image=None)

    def __str__(self):
        return self.title

# --- 4. ProductImage (Gallery) ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        is_new_upload = False
        if self.image:
            if not self.pk:
                is_new_upload = True
            else:
                old_obj = ProductImage.objects.filter(pk=self.pk).first()
                if old_obj and old_obj.image != self.image:
                    is_new_upload = True

        super().save(*args, **kwargs)

        if is_new_upload:
            url = upload_to_imgbb(self.image)
            if url:
                cleanup_local_file(self, 'image')
                ProductImage.objects.filter(pk=self.pk).update(image_url=url, image=None)

    def __str__(self):
        return f"Gallery Image for {self.product.title}"
