import os
from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from .utils import upload_to_imgbb

# --- HELPER FUNCTION TO KILL MACHINE FILES ---
def cleanup_local_file(instance, field_name):
    """मशीन से फिजिकल फाइल डिलीट करने के लिए"""
    try:
        file_field = getattr(instance, field_name)
        if file_field and os.path.exists(file_field.path):
            os.remove(file_field.path)
    except Exception:
        pass

# --- 1. HomeSlider ---
class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='sliders/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_new = False
        if not self.id and self.image: is_new = True
        elif self.id:
            try:
                old = HomeSlider.objects.get(id=self.id).image
                if self.image and self.image != old: is_new = True
            except: is_new = True

        super().save(*args, **kwargs)
        if is_new:
            url = upload_to_imgbb(self.image)
            if url:
                cleanup_local_file(self, 'image') # मशीन से फाइल डिलीट
                HomeSlider.objects.filter(id=self.id).update(image_url=url, image=None)

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
        is_new = False
        if not self.id and self.image: is_new = True
        elif self.id:
            try:
                old = Category.objects.get(id=self.id).image
                if self.image and self.image != old: is_new = True
            except: is_new = True

        super().save(*args, **kwargs)
        if is_new:
            url = upload_to_imgbb(self.image)
            if url:
                cleanup_local_file(self, 'image')
                Category.objects.filter(id=self.id).update(image_url=url, image=None)

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
        is_new = False
        if not self.id and self.main_image: is_new = True
        elif self.id:
            try:
                old = Product.objects.get(id=self.id).main_image
                if self.main_image and self.main_image != old: is_new = True
            except: is_new = True

        super().save(*args, **kwargs)
        if is_new:
            url = upload_to_imgbb(self.main_image)
            if url:
                cleanup_local_file(self, 'main_image')
                Product.objects.filter(id=self.id).update(main_image_url=url, main_image=None)

    def __str__(self):
        return self.title

# --- 4. ProductImage ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        is_new = False
        if not self.id and self.image: is_new = True
        elif self.id:
            try:
                old = ProductImage.objects.get(id=self.id).image
                if self.image and self.image != old: is_new = True
            except: is_new = True

        super().save(*args, **kwargs)
        if is_new:
            url = upload_to_imgbb(self.image)
            if url:
                cleanup_local_file(self, 'image')
                ProductImage.objects.filter(id=self.id).update(image_url=url, image=None)

    def __str__(self):
        return f"Gallery Image for {self.product.title}"
