from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from .utils import upload_to_imgbb  # utils.py से फंक्शन इम्पोर्ट करें

# --- 1. HomeSlider ---
class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    # help_text बदल दिया है ताकि तुझे याद रहे
    image = models.ImageField(upload_to='sliders/', null=True, blank=True, help_text="इमेज चुनें, अपलोड के बाद यह सर्वर से हट जाएगी और सिर्फ ImgBB लिंक रहेगा")
    image_url = models.URLField(max_length=500, blank=True, null=True) 
    link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # अगर नई इमेज चुनी गई है, तो उसे ImgBB पर भेजें
        if self.image:
            url = upload_to_imgbb(self.image)
            if url: 
                self.image_url = url
                self.image = None # मीडिया फोल्डर से फाइल का नाम हटा दें
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or f"Slider {self.id}"

# --- 2. Category ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.image:
            url = upload_to_imgbb(self.image)
            if url: 
                self.image_url = url
                self.image = None # जड़ से खत्म
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"

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
        if not self.slug:
            self.slug = slugify(self.title)
        if self.main_image:
            url = upload_to_imgbb(self.main_image)
            if url: 
                self.main_image_url = url
                self.main_image = None # सिर्फ ImgBB लिंक बचेगा
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- 4. ProductImage (Multiple Images) ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        if self.image:
            url = upload_to_imgbb(self.image)
            if url: 
                self.image_url = url
                self.image = None # फाइल उड़ने का डर खत्म
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.title}"
