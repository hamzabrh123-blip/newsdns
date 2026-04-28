import os
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor_uploader.fields import RichTextUploadingField
from .utils import upload_to_imgbb

# --- 1. HomeSlider ---
class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='sliders/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

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
    main_image = models.ImageField(upload_to='products/main/', null=True, blank=True)
    main_image_url = models.URLField(max_length=500, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- 4. ProductImage (Gallery) ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)

# --- SIGNALS FOR IMGBB UPLOAD ---

@receiver(post_save, sender=HomeSlider)
@receiver(post_save, sender=Category)
@receiver(post_save, sender=Product)
@receiver(post_save, sender=ProductImage)
def handle_imgbb_upload(sender, instance, created, **kwargs):
    """
    यह सिग्नल चेक करेगा कि कौन सा मॉडल है और उसकी इमेज को IMGBB पर भेज देगा।
    """
    # 1. फील्ड का नाम तय करें (Product में 'main_image' है, बाकी में 'image')
    image_field_name = 'main_image' if sender == Product else 'image'
    url_field_name = 'main_image_url' if sender == Product else 'image_url'
    
    image_file = getattr(instance, image_field_name)

    # अगर इमेज फाइल मौजूद है, तो उसे अपलोड करें
    if image_file and hasattr(image_file, 'path'):
        try:
            url = upload_to_imgbb(image_file)
            if url:
                # लोकल फाइल का पाथ सुरक्षित करें
                path = image_file.path
                
                # Database अपडेट करें (बिना save() कॉल किए ताकि loop न बने)
                sender.objects.filter(pk=instance.pk).update(**{
                    url_field_name: url,
                    image_field_name: None
                })
                
                # लोकल फाइल डिलीट करें
                if os.path.exists(path):
                    os.remove(path)
                    print(f"✅ Successfully uploaded and deleted local file for {sender.__name__}")
        except Exception as e:
            print(f"❌ Error in Signal for {sender.__name__}: {e}")
