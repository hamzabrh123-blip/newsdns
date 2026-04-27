from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField # CKEditor के लिए



class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='sliders/')
    link = models.URLField(max_length=500, blank=True, help_text="स्लाइड पर क्लिक करने पर कहाँ जाना है?")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title if self.title else f"Slider {self.id}"


# 1. Category मॉडल (यह सबसे ऊपर रहेगा)

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

# 2. Product मॉडल (यह ProductImage के ऊपर होना चाहिए)
class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Product Name")
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Prices
    old_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Market Price (MRP)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Our Selling Price")
    
    # Product क्लास के अंदर कहीं भी जोड़ दें
    buy_now_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Direct Buy Link (External)")


    # Content (AdSense Booster)
    short_description = models.TextField(max_length=500, help_text="Search Result me dikhne ke liye")
    long_description = RichTextUploadingField(verbose_name="Full Product Details & Review") 

    # Media
    main_image = models.ImageField(upload_to='products/main/')
    
    # Meta Details
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, verbose_name="Home Page par dikhayein?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# 3. ProductImage मॉडल (यह सबसे नीचे रहेगा ताकि इसे Product क्लास मिल सके)
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True, help_text="जैसे: फ्रंट व्यू, बैक व्यू")

    def __str__(self):
        return f"Image for {self.product.title}"