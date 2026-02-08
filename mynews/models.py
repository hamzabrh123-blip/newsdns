import uuid, io
from PIL import Image
from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from django.urls import reverse
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from .utils import upload_to_imgbb 

class News(models.Model):
    # 'UP' hata diya hai, ab sirf city name hai
    LOCATION_DATA = [
        ('Agra', 'आगरा'), ('Aligarh', 'अलीगढ़'), ('Ambedkar-Nagar', 'अम्बेडकर नगर'), 
        ('Amethi', 'अमेठी'), ('Amroha', 'अमरोहा'), ('Auraiya', 'औरैया'), 
        ('Ayodhya', 'अयोध्या'), ('Azamgarh', 'आजमगढ़'), ('Baghpat', 'बागपत'), 
        ('Bahraich', 'बहराइच'), ('Ballia', 'बलिया'), ('Balrampur', 'बालरामपुर'), 
        ('Banda', 'बांदा'), ('Barabanki', 'बाराबंकी'), ('Bareilly', 'बरेली'), 
        ('Basti', 'बस्ती'), ('Bhadohi', 'भदोही'), ('Bijnor', 'बिजनौर'), 
        ('Budaun', 'बदायूँ'), ('Bulandshahr', 'बुलंदशहर'), ('Chandauli', 'चंदौली'), 
        ('Chitrakoot', 'चित्रकूट'), ('Deoria', 'देवरिया'), ('Etah', 'एटा'), 
        ('Etawah', 'इटावा'), ('Farrukhabad', 'फर्रुखाबाद'), ('Fatehpur', 'फतेहपुर'), 
        ('Firozabad', 'फिरोजाबाद'), ('Gautam-Buddha-Nagar', 'नोएडा'), 
        ('Ghaziabad', 'गाजियाबाद'), ('Ghazipur', 'गाजीपुर'), ('Gonda', 'गोंडा'), 
        ('Gorakhpur', 'गोरखपुर'), ('Hamirpur', 'हमीरपुर'), ('Hapur', 'हापुड़'), 
        ('Hardoi', 'हरदोई'), ('Hathras', 'हाथरास'), ('Jalaun', 'जालौन'), 
        ('Jaunpur', 'जाँयपुर'), ('Jhansi', 'झाँसी'), ('Kannauj', 'कन्नौज'), 
        ('Kanpur-Dehat', 'कानपुर देहात'), ('Kanpur-Nagar', 'कानपुर नगर'), 
        ('Kasganj', 'कासगंज'), ('Kaushambi', 'कौशाम्बी'), ('Kushinagar', 'कुशीनगर'), 
        ('Lakhimpur-Kheri', 'लखीमपुर खीरी'), ('Lalitpur', 'ललितपुर'), 
        ('Lucknow', 'लखनऊ'), ('Maharajganj', 'महराजगंज'), ('Mahoba', 'महोबा'), 
        ('Mainpuri', 'मैनपुरी'), ('Mathura', 'मथुरा'), ('Mau', 'मऊ'), 
        ('Meerut', 'मेरठ'), ('Mirzapur', 'मिर्जापुर'), ('Moradabad', 'मुरादाबाद'), 
        ('Muzaffarnagar', 'मुजफ्फरनगर'), ('Pilibhit', 'पीलीभीत'), ('Pratapgarh', 'प्रतापगढ़'), 
        ('Prayagraj', 'प्रयागराज'), ('Rae-Bareli', 'रायबरेली'), ('Rampur', 'रामपुर'), 
        ('Saharanpur', 'सहारनपुर'), ('Sambhal', 'सम्भल'), ('Sant-Kabir-Nagar', 'संत कबीर नगर'), 
        ('Shahjahanpur', 'शाहजहांपुर'), ('Shamli', 'शामली'), ('Shravasti', 'श्रावस्ती'), 
        ('Siddharthnagar', 'सिद्धार्थनगर'), ('Sitapur', 'सीतापुर'), ('Sonbhadra', 'सोनभद्र'), 
        ('Sultanpur', 'सुलतानपुर'), ('Unnao', 'उन्नाव'), ('Varanasi', 'वाराणसी'),
        
        ('Delhi', 'दिल्ली'), ('National', 'राष्ट्रीय खबर'),
        ('International', 'अंतर्राष्ट्रीय'), ('Sports', 'खेल समाचार'),
        ('Bollywood', 'बॉलीवुड'), ('Technology', 'टेक्नोलॉजी'), 
        ('Market', 'मार्केट भाव'),
    ]

    title = models.CharField(max_length=250)
    status = models.CharField(max_length=20, choices=[('Draft', 'Draft'), ('Published', 'Published')], default='Draft')
    category = models.CharField(max_length=100, blank=True, null=True)
    url_city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, choices=[(x[0], x[1]) for x in LOCATION_DATA], blank=True, null=True)
    content = RichTextField(blank=True) 
    image = models.ImageField(upload_to="news_pics/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    date = models.DateTimeField(default=now)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    is_important = models.BooleanField(default=False, verbose_name="Breaking News?")
    meta_keywords = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'mynews_news'

    def get_absolute_url(self):
        city = self.url_city if self.url_city else "news"
        return reverse('news_detail', kwargs={'url_city': city, 'slug': self.slug})

    def save(self, *args, **kwargs):
        # 1. District and City Logic (No 'UP' clutter)
        if self.district:
            for eng, hin in self.LOCATION_DATA:
                if self.district == eng:
                    self.url_city = eng.lower()
                    self.category = hin
                    break
        
        # 2. Watermark and ImgBB Logic
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Watermark logic
                watermark_path = finders.find('watermark.png')
                if watermark_path:
                    watermark = Image.open(watermark_path).convert("RGBA")
                    # Logo size relative to image
                    base_side = min(img.width, img.height)
                    target_width = int(base_side * 0.20) 
                    w_ratio = target_width / float(watermark.size[0])
                    target_height = int(float(watermark.size[1]) * float(w_ratio))
                    watermark = watermark.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    
                    # Bottom-Right placement
                    position = (img.width - target_width - 20, img.height - target_height - 20)
                    img.paste(watermark, position, watermark)

                # Memory buffer for ImgBB
                output = io.BytesIO()
                img.save(output, format='WEBP', quality=70)
                output.seek(0)
                
                temp_file = ContentFile(output.read(), name=f"{uuid.uuid4().hex[:10]}.webp")
                
                # Direct ImgBB upload
                uploaded_link = upload_to_imgbb(temp_file)
                if uploaded_link:
                    self.image_url = uploaded_link
                    self.image = None # Local storage bachane ke liye
            except Exception as e:
                print(f"Bhai Error: {e}")

        # 3. Slug logic
        if not self.slug:
            clean_text = unidecode(self.title)
            self.slug = f"{slugify(clean_text)[:60]}-{str(uuid.uuid4())[:6]}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
