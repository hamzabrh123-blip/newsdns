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
    LOCATION_DATA = [
        ('Agra', 'आगरा', 'agra'), ('Aligarh', 'अलीगढ़', 'aligarh'), ('Ambedkar-Nagar', 'अम्बेडकर नगर', 'ambedkar-nagar'), 
        ('Amethi', 'अमेठी', 'amethi'), ('Amroha', 'अमरोहा', 'amroha'), ('Auraiya', 'औरैया', 'auraiya'), 
        ('Ayodhya', 'अयोध्या', 'ayodhya'), ('Azamgarh', 'आजमगढ़', 'azamgarh'), ('Baghpat', 'बागपत', 'baghpat'), 
        ('Bahraich', 'बहराइच', 'bahraich'), ('Ballia', 'बलिया', 'ballia'), ('Balrampur', 'बालरामपुर', 'balrampur'), 
        ('Banda', 'बांदा', 'banda'), ('Barabanki', 'बाराबंकी', 'barabanki'), ('Bareilly', 'बरेली', 'bareilly'), 
        ('Basti', 'बस्ती', 'basti'), ('Bhadohi', 'भदोही', 'bhadohi'), ('Bijnor', 'बिजनौर', 'bijnor'), 
        ('Budaun', 'बदायूँ', 'budaun'), ('Bulandshahr', 'बुलंदशहर', 'bulandshahr'), ('Chandauli', 'चंदौली', 'chandauli'), 
        ('Chitrakoot', 'चित्रकूट', 'chitrakoot'), ('Deoria', 'देवरिया', 'deoria'), ('Etah', 'एटा', 'etah'), 
        ('Etawah', 'इटावा', 'etawah'), ('Farrukhabad', 'फर्रुखाबाद', 'farrukhabad'), ('Fatehpur', 'फतेहपुर', 'fatehpur'), 
        ('Firozabad', 'फिरोजाबाद', 'firozabad'), ('Gautam-Buddha-Nagar', 'नोएडा', 'gautam-buddha-nagar'), 
        ('Ghaziabad', 'गाजियाबाद', 'ghaziabad'), ('Ghazipur', 'गाजीपुर', 'ghazipur'), ('Gonda', 'गोंडा', 'gonda'), 
        ('Gorakhpur', 'गोरखपुर', 'gorakhpur'), ('Hamirpur', 'हमीरपुर', 'hamirpur'), ('Hapur', 'हापुड़', 'hapur'), 
        ('Hardoi', 'हरदोई', 'hardoi'), ('Hathras', 'हाथरास', 'hathras'), ('Jalaun', 'जालौन', 'jalaun'), 
        ('Jaunpur', 'जाँयपुर', 'jaunpur'), ('Jhansi', 'झाँसी', 'jhansi'), ('Kannauj', 'कन्नौज', 'kannauj'), 
        ('Kanpur-Dehat', 'कानपुर देहात', 'kanpur-dehat'), ('Kanpur-Nagar', 'कानपुर नगर', 'kanpur-nagar'), 
        ('Kasganj', 'कासगंज', 'kasganj'), ('Kaushambi', 'कौशाम्बी', 'kaushambi'), ('Kushinagar', 'कुशीनगर', 'kushinagar'), 
        ('Lakhimpur-Kheri', 'लखीमपुर खीरी', 'lakhimpur-kheri'), ('Lalitpur', 'ललितपुर', 'lalitpur'), 
        ('Lucknow', 'लखनऊ', 'lucknow'), ('Maharajganj', 'महराजगंज', 'maharajganj'), ('Mahoba', 'महोबा', 'mahoba'), 
        ('Mainpuri', 'मैनपुरी', 'mainpuri'), ('Mathura', 'मथुरा', 'mathura'), ('Mau', 'मऊ', 'mau'), 
        ('Meerut', 'मेरठ', 'meerut'), ('Mirzapur', 'मिर्जापुर', 'mirzapur'), ('Moradabad', 'मुरादाबाद', 'moradabad'), 
        ('Muzaffarnagar', 'मुजफ्फरनगर', 'muzaffarnagar'), ('Pilibhit', 'पीलीभीत', 'pilibhit'), ('Pratapgarh', 'प्रतापगढ़', 'pratapgarh'), 
        ('Prayagraj', 'प्रयागराज', 'prayagraj'), ('Rae-Bareli', 'रायबरेली', 'rae-bareli'), ('Rampur', 'रामपुर', 'rampur'), 
        ('Saharanpur', 'सहारनपुर', 'saharanpur'), ('Sambhal', 'सम्भल', 'sambhal'), ('Sant-Kabir-Nagar', 'संत कबीर नगर', 'sant-kabir-nagar'), 
        ('Shahjahanpur', 'शाहजहांपुर', 'shahjahanpur'), ('Shamli', 'शामली', 'shamli'), ('Shravasti', 'श्रावस्ती', 'shravasti'), 
        ('Siddharthnagar', 'सिद्धार्थनगर', 'siddharthnagar'), ('Sitapur', 'सीतापुर', 'sitapur'), ('Sonbhadra', 'सोनभद्र', 'sonbhadra'), 
        ('Sultanpur', 'सुलतानपुर', 'sultanpur'), ('Unnao', 'उन्नाव', 'unnao'), ('Varanasi', 'वाराणसी', 'varanasi'),
        ('Delhi', 'दिल्ली', 'delhi'), ('National', 'राष्ट्रीय खबर', 'national'),
        ('International', 'अंतर्राष्ट्रीय', 'international'), ('Sports', 'खेल समाचार', 'sports'),
        ('Bollywood', 'बॉलीवुड', 'bollywood'), ('Technology', 'टेक्नोलॉजी', 'technology'), 
        ('Market', 'मार्केट भाव', 'market') ,
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
        # 1. Date Fix (AdSense ke liye zaroori hai bhai)
        if not self.date:
            self.date = now()

        # 2. Category & City Logic (Ye news dikhane ke liye chahiye)
        if self.district:
            for eng, hin, city_slug in self.LOCATION_DATA:
                if self.district == eng:
                    self.url_city = city_slug
                    self.category = hin
                    break
        
        # 3. WATERMARK + IMGBB (Only this, no extra drama)
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)
                
                # RGBA to RGB (Crash se bachne ke liye)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Watermark Lagana
                watermark_path = finders.find('watermark.png')
                if watermark_path:
                    watermark = Image.open(watermark_path).convert("RGBA")
                    # Image ka 20% size ka watermark
                    w_size = int(min(img.width, img.height) * 0.20)
                    w_ratio = w_size / float(watermark.size[0])
                    h_size = int(float(watermark.size[1]) * float(w_ratio))
                    watermark = watermark.resize((w_size, h_size), Image.Resampling.LANCZOS)
                    
                    # Position: Bottom Right
                    img.paste(watermark, (img.width - w_size - 20, img.height - h_size - 20), watermark)
                    watermark.close() # RAM khali karo

                # Save to Buffer (No WebP, original quality)
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=90)
                output.seek(0)
                img.close() # RAM khali karo

                # ImgBB par bhejo
                temp_file = ContentFile(output.read(), name=self.image.name)
                uploaded_link = upload_to_imgbb(temp_file)
                if uploaded_link:
                    self.image_url = uploaded_link
                    self.image = None # Local space khali
            except Exception as e:
                print(f"Error: {e}")

        # 4. Slug (Simple wala)
        if not self.slug:
            try:
                self.slug = f"{slugify(unidecode(self.title))[:60]}-{str(uuid.uuid4())[:6]}"
            except:
                self.slug = f"news-{str(uuid.uuid4())[:8]}"

        super().save(*args, **kwargs)
