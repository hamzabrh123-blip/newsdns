import uuid
import time
import requests
import json
import random
import string

from django.db import models
from django.conf import settings
from django.utils.text import slugify

from ckeditor_uploader.fields import RichTextUploadingField
from unidecode import unidecode
from urllib.parse import urlparse, urlunparse

from .utils import process_and_upload_to_imgbb, ping_google_indexing


# ==========================================
# HELPER FUNCTIONS (URL & IMAGE CLEANING)
# ==========================================

def clean_image_url(url):
    """Image URL se ? aur uske baad ka saara kachra hata deta hai"""
    if not url:
        return url
    base_url = url.split('?')[0]
    parsed = urlparse(base_url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))


def clean_amazon_link(url, tracking_id="uttarworld202-21"):
    """Amazon ke link ko clean karke sirf standard ASIN aur official tag rakhta hai"""
    if not url or "amazon" not in url:
        return url
    parsed = urlparse(url)
    path_parts = parsed.path.split('/')
    asin = None
    for i, part in enumerate(path_parts):
        if part == 'dp' and i + 1 < len(path_parts):
            asin = path_parts[i+1]
            break
        elif part == 'gp' and i + 2 < len(path_parts) and path_parts[i+1] == 'product':
            asin = path_parts[i+2]
            break
    clean_path = f"/dp/{asin}" if asin else parsed.path
    return urlunparse((
        parsed.scheme or 'https',
        parsed.netloc or 'www.amazon.in',
        clean_path, '', f'tag={tracking_id}', ''
    ))


# ==========================================
# BING INDEXING HELPER FUNCTIONS
# ==========================================

def ping_bing_indexing(url):
    api_key = getattr(settings, "BING_API_KEY", "")
    if not api_key:
        return False
    endpoint = f"https://bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey={api_key}"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {"siteUrl": "https://uttarworld.com", "urlList": [url]}
    try:
        response = requests.post(endpoint, data=json.dumps(payload), headers=headers, timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def ping_bing_indexing_batch(urls):
    api_key = getattr(settings, "BING_API_KEY", "")
    if not api_key:
        return False
    endpoint = f"https://bing.com/webmaster/api.svc/json/SubmitUrlbatch?apikey={api_key}"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    urls = list(dict.fromkeys(url for url in urls if url))
    if not urls:
        return False
    batch_size = 500
    total_urls = len(urls)
    submitted_urls = 0
    for start in range(0, total_urls, batch_size):
        batch = urls[start:start + batch_size]
        payload = {"siteUrl": "https://uttarworld.com", "urlList": batch}
        try:
            response = requests.post(endpoint, data=json.dumps(payload), headers=headers, timeout=30)
            if response.status_code == 200:
                submitted_urls += len(batch)
        except Exception:
            pass
    return submitted_urls == total_urls


def submit_all_products_to_bing():
    products = Product.objects.filter(is_available=True).exclude(slug__isnull=True).exclude(slug="").only("slug")
    urls = [f"https://uttarworld.com/shopping/product/{product.slug}/" for product in products]
    return ping_bing_indexing_batch(urls)


# ==========================================
# 1. STORE LOGO UPLOAD
# ==========================================

class StoreLogoUpload(models.Model):
    logo_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Logo {self.id}"


# ==========================================
# 2. PINTEREST POST
# ==========================================

class PinterestPost(models.Model):
    title = models.CharField(max_length=255)
    image_url = models.URLField(max_length=500)
    link = models.URLField(max_length=500)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image_url:
            self.image_url = clean_image_url(self.image_url)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ==========================================
# 3. CATEGORY
# ==========================================

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    description = RichTextUploadingField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return f"/shopping/category/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        
        # Clean image URL if provided
        if self.image_url:
            self.image_url = clean_image_url(self.image_url)
            
        image_url_val = str(self.image_url) if self.image_url else ""
        is_new_image = bool(self.image and not image_url_val)
        
        super().save(*args, **kwargs)
        
        if is_new_image:
            self.handle_upload()

        target_url = f"https://uttarworld.com{self.get_absolute_url()}"
        try:
            ping_google_indexing(target_url)
            ping_bing_indexing(target_url)
        except Exception:
            pass

    def handle_upload(self):
        try:
            new_url = process_and_upload_to_imgbb(self, is_shop=True)
            if new_url:
                Category.objects.filter(pk=self.pk).update(image_url=clean_image_url(new_url), image=None)
        except Exception:
            pass

    def __str__(self):
        return self.name


# ==========================================
# 4. PRODUCT MANAGER
# ==========================================

class ProductManager(models.Manager):
    def search_and_filter(self, query=None, max_price=None):
        queryset = self.get_queryset().filter(is_available=True)
        if query:
            queryset = queryset.filter(title__icontains=query)
        if max_price and str(max_price).isdigit():
            queryset = queryset.filter(
                models.Q(selling_price__lte=int(max_price)) | 
                models.Q(mrp_price__lte=int(max_price))
            )
        return queryset.distinct()


# ==========================================
# 5. PRODUCT
# ==========================================

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50, unique=True, blank=True, help_text="Automatically generated short random code slug")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    
    store_name = models.CharField(max_length=100, blank=True, null=True, help_text="Store name (e.g., Amazon, Meesho)")
    
    mrp_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Default MRP (Optional)")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Default Selling Price")
    
    default_color = models.CharField(max_length=50, blank=True, null=True, help_text="Default Color")
    default_size = models.CharField(max_length=50, blank=True, null=True, help_text="Default Size / Weight")

    CURRENCY_CHOICES = [
        ("₹", "INR (₹)"),
        ("$", "USD ($)"),
        ("€", "EUR (€)")
    ]
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default="₹")

    long_description = RichTextUploadingField()
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    def get_absolute_url(self):
        return f"/shopping/product/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            while True:
                random_slug = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                if not Product.objects.filter(slug=random_slug).exists():
                    self.slug = random_slug
                    break

        super().save(*args, **kwargs)

        target_url = f"https://uttarworld.com{self.get_absolute_url()}"
        try:
            ping_google_indexing(target_url)
            ping_bing_indexing(target_url)
        except Exception:
            pass

    def __str__(self):
        return self.title


# ==========================================
# 6. PRODUCT VARIANT (Flexible Selling Price)
# ==========================================

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Variant Image URL")
    video_url = models.URLField(max_length=500, blank=True, null=True, help_text="Variant Video URL")
    earn_karo_url = models.URLField(max_length=1000, blank=True, null=True, help_text="Affiliate / EarnKaro / Amazon Link")
    
    # Selling price ab CharField hai, ab yahan range ya single price kuch bhi daal sakta hai
    selling_price = models.CharField(max_length=100, help_text="Variant Selling Price (e.g., 355 or 355 ~ 390)")
    size = models.CharField(max_length=50, blank=True, null=True, help_text="Size / Weight")
    colour = models.CharField(max_length=50, blank=True, null=True, help_text="Colour")
    mrp_price = models.CharField(max_length=100, blank=True, null=True, help_text="MRP Price")

    def save(self, *args, **kwargs):
        # 1. Image URL clean karo (? ke baad ka kachra gayab)
        if self.image_url:
            self.image_url = clean_image_url(self.image_url)
            
        # 2. Agar link Amazon ka hai toh automatically clean karke tag laga do
        if self.earn_karo_url and "amazon" in self.earn_karo_url.lower():
            self.earn_karo_url = clean_amazon_link(self.earn_karo_url, tracking_id="uttarworld202-21")
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.title} - {self.size or self.colour or 'Variant'} ({self.selling_price})"

# ==========================================
# 7. HOME SLIDER
# ==========================================

class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="sliders/", null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.image_url:
            self.image_url = clean_image_url(self.image_url)
            
        image_url_val = str(self.image_url) if self.image_url else ""
        is_new_file = bool(self.image and not image_url_val)
        super().save(*args, **kwargs)
        if is_new_file:
            self.handle_upload()

    def handle_upload(self):
        try:
            new_url = process_and_upload_to_imgbb(self, is_shop=True)
            if new_url:
                HomeSlider.objects.filter(pk=self.pk).update(image_url=clean_image_url(new_url), image=None)
        except Exception:
            pass

    def __str__(self):
        return self.title if self.title else f"Slider {self.id}"


# ==========================================
# 8. DROPDOWN MENU
# ==========================================

class DropdownMenu(models.Model):
    menu_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    categories = models.ManyToManyField(Category, related_name="dropdown_menus")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.menu_name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.menu_name


# ==========================================
# 9. HOME SECTION
# ==========================================

class HomeSection(models.Model):
    image = models.ImageField(upload_to="home_sections/", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="home_sections", null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.category.name if self.category else "Home Section"


# ==========================================
# 10. HOMEPAGE SEO
# ==========================================

class HomePageSEO(models.Model):
    title = models.CharField(max_length=255)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)
    seo_content = RichTextUploadingField(blank=True, null=True)
    og_image = models.ImageField(upload_to="seo/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Homepage SEO"


# ==========================================
# 11. STORE CONFIGURATION
# ==========================================

class StoreConfiguration(models.Model):
    store_name = models.CharField(max_length=100, unique=True)
    default_coupon_code = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.store_name