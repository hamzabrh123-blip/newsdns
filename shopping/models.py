import uuid
import time
from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from unidecode import unidecode
from .utils import process_and_upload_to_imgbb, ping_google_indexing

# --- 1. HomeSlider ---
class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='sliders/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        url_val = str(self.image_url) if self.image_url else ""
        is_new_img = bool(self.image and "i.ibb.co" not in url_val)
        super().save(*args, **kwargs)
        if is_new_img:
            self.handle_upload()

    def handle_upload(self):
        try:
            new_url = process_and_upload_to_imgbb(self, is_shop=True)
            if new_url:
                HomeSlider.objects.filter(pk=self.pk).update(image_url=new_url, image=None)
        except Exception as e:
            print(f"Slider Error: {e}")

    def __str__(self):
        return self.title if self.title else f"Slider {self.id}"

# --- 2. Category ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    description = RichTextUploadingField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug: 
            self.slug = slugify(unidecode(self.name))
        url_val = str(self.image_url) if self.image_url else ""
        is_new_img = bool(self.image and "i.ibb.co" not in url_val)
        super().save(*args, **kwargs)
        if is_new_img: 
            self.handle_upload()

    def handle_upload(self):
        try:
            new_url = process_and_upload_to_imgbb(self, is_shop=True)
            if new_url: 
                Category.objects.filter(pk=self.pk).update(image_url=new_url, image=None)
        except Exception as e: 
            print(f"Category Error: {e}")

    def __str__(self): return self.name

# --- 3. Product ---
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    mrp_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_display = models.CharField(max_length=100)
    long_description = RichTextUploadingField() 
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return f"/product/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))[:80]}-{str(uuid.uuid4())[:6]}"
        super().save(*args, **kwargs)
        try:
            ping_google_indexing(f"https://uttarworld.com{self.get_absolute_url()}")
        except Exception as e:
            print(f"Indexing Error: {e}")

    def __str__(self): return self.title

# --- 4. ProductVariant ---
class ProductVariant(models.Model):
    product = models.ForeignKey('Product', related_name='variants', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='variants/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    earn_karo_url = models.URLField(max_length=700)
    variant_code = models.CharField(max_length=20, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.variant_code:
            prefix = "".join([word[0] for word in self.product.title.split()[:2]]).upper()
            self.variant_code = f"{prefix}-{str(uuid.uuid4())[:4].upper()}"
        super().save(*args, **kwargs)
        if self.image and "i.ibb.co" not in str(self.image_url):
            self.handle_variant_upload()

    def handle_variant_upload(self):
        try:
            time.sleep(0.5)
            new_url = process_and_upload_to_imgbb(self, is_shop=True)
            if new_url:
                self.image_url = new_url
                self.image = None
                super().save(update_fields=['image_url', 'image'])
        except Exception as e:
            print(f"Variant Upload Error: {e}")

    def __str__(self): return f"{self.product.title} - {self.variant_code}"

# --- 5. VariantStoreCoupon ---
class VariantStoreCoupon(models.Model):
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE, related_name='coupons')
    store_name = models.CharField(max_length=100, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    coupon_code = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        if self.store_name and not self.coupon_code:
            from .models import StoreConfiguration 
            config = StoreConfiguration.objects.filter(store_name__iexact=self.store_name).first()
            if config:
                self.coupon_code = config.default_coupon_code
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.store_name} - {self.coupon_code}"

# --- 6. DropdownMenu ---
class DropdownMenu(models.Model):
    menu_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='dropdown_menus')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(unidecode(self.menu_name))
        super().save(*args, **kwargs)

    def __str__(self): return self.menu_name