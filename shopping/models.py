import os
from django.db import models, transaction
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

    def __str__(self):
        return f"Gallery for {self.product.title}"


# --- 100% WORKING SIGNAL LOGIC ---

@receiver(post_save, sender=HomeSlider)
@receiver(post_save, sender=Category)
@receiver(post_save, sender=Product)
@receiver(post_save, sender=ProductImage)
def handle_imgbb_upload_secure(sender, instance, **kwargs):
    """
    यह सिग्नल ट्रांजेक्शन कमिट होने का इंतज़ार करेगा ताकि हैवी इमेजेस प्रोसेस हो सकें।
    """
    # फील्ड्स का नाम सही से चुनें
    if sender == Product:
        img_field = 'main_image'
        url_field = 'main_image_url'
    else:
        img_field = 'image'
        url_field = 'image_url'

    image_file = getattr(instance, img_field)

    # अगर फाइल लोकल स्टोरेज में है, तभी आगे बढ़ें
    if image_file and hasattr(image_file, 'path') and os.path.exists(image_file.path):
        
        # 'do_upload' फंक्शन तभी चलेगा जब Django का सेव ऑपरेशन पूरा हो जाए
        def do_upload():
            try:
                # इमेजबॉन्ड्स के लिए utils फंक्शन कॉल करें
                new_url = upload_to_imgbb(image_file)
                
                if new_url:
                    local_path = image_file.path
                    
                    # बिना save() ट्रिगर किए डेटाबेस अपडेट (ताकि Recursion न हो)
                    sender.objects.filter(pk=instance.pk).update(**{
                        url_field: new_url,
                        img_field: None
                    })
                    
                    # लोकल फाइल डिलीट करें
                    if os.path.exists(local_path):
                        os.remove(local_path)
                        print(f"✅ Successfully Uploaded: {sender.__name__} (ID: {instance.pk})")
            except Exception as e:
                print(f"❌ Upload Failed for {sender.__name__}: {e}")

        # Render और हैवी लोड के लिए सबसे सुरक्षित तरीका
        transaction.on_commit(do_upload)
