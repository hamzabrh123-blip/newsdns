from django.db import models, transaction
from django.utils.text import slugify
from .utils import upload_to_imgbb # इसमें अब Logo + WebP वाला कोड डालना

# --- 1. HomeSlider ---
class HomeSlider(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='sliders/', null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True) 
    
    def save(self, *args, **kwargs):
        # पक्का करो कि नई इमेज आई है
        is_new = True if self.image and not self.image_url else False
        super().save(*args, **kwargs)
        
        if is_new:
            # न्यूज़ मॉडल की तरह ट्रांजैक्शन कमिट होने पर हैंडल करो
            transaction.on_commit(lambda: self.process_image())

    def process_image(self):
        # यहाँ utils वाला फंक्शन Branding (Logo + WebP) करेगा
        url = upload_to_imgbb(self.image)
        if url:
            HomeSlider.objects.filter(id=self.id).update(image_url=url, image=None)

# --- 2. Product --- (बाकी मॉडल्स में भी यही पैटर्न रहेगा)
class Product(models.Model):
    title = models.CharField(max_length=255)
    main_image = models.ImageField(upload_to='products/', null=True, blank=True)
    main_image_url = models.URLField(max_length=500, blank=True, null=True)
    # ... बाकी फील्ड्स ...

    def save(self, *args, **kwargs):
        is_new = True if self.main_image and not self.main_image_url else False
        super().save(*args, **kwargs)
        if is_new:
            transaction.on_commit(lambda: self.process_main_image())

    def process_main_image(self):
        url = upload_to_imgbb(self.main_image)
        if url:
            Product.objects.filter(id=self.id).update(main_image_url=url, main_image=None)
