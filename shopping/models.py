from django.db import models, transaction
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from .utils import upload_to_imgbb

# --- 1. HomeSlider (बैनर के लिए) ---
class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='sliders/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_new = True if self.image and not self.image_url else False
        super().save(*args, **kwargs)
        if is_new:
            transaction.on_commit(lambda: self.handle_slider_upload())

    def handle_slider_upload(self):
        # यहाँ utils वाला फंक्शन Logo और WebP का तड़का लगाएगा
        url = upload_to_imgbb(self.image)
        if url:
            HomeSlider.objects.filter(id=self.id).update(image_url=url, image=None)

    def __str__(self):
        return self.title or f"Slider {self.id}"


# --- 2. Category (कैटेगरी के लिए) ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        is_new = True if self.image and not self.image_url else False
        super().save(*args, **kwargs)
        if is_new:
            transaction.on_commit(lambda: self.handle_cat_upload())

    def handle_cat_upload(self):
        url = upload_to_imgbb(self.image)
        if url:
            Category.objects.filter(id=self.id).update(image_url=url, image=None)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# --- 3. Product (मेन प्रोडक्ट) ---
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
        is_new = True if self.main_image and not self.main_image_url else False
        super().save(*args, **kwargs)
        if is_new:
            transaction.on_commit(lambda: self.handle_product_main_upload())

    def handle_product_main_upload(self):
        url = upload_to_imgbb(self.main_image)
        if url:
            Product.objects.filter(id=self.id).update(main_image_url=url, main_image=None)

    def __str__(self):
        return self.title


# --- 4. ProductImage (एक्स्ट्रा गैलरी फोटो के लिए) ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        is_new = True if self.image and not self.image_url else False
        super().save(*args, **kwargs)
        if is_new:
            transaction.on_commit(lambda: self.handle_gallery_upload())

    def handle_gallery_upload(self):
        url = upload_to_imgbb(self.image)
        if url:
            ProductImage.objects.filter(id=self.id).update(image_url=url, image=None)

    def __str__(self):
        return f"Gallery Image for {self.product.title}"
