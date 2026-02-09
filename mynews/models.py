import uuid, io, os, gc
from PIL import Image
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings
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
        ('Jaunpur', 'जूनपुर', 'jaunpur'), ('Jhansi', 'झाँसी', 'jhansi'), ('Kannauj', 'कन्नौज', 'kannauj'), 
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
        ('Bollywood', 'बॉलीवुड', 'bollywood'), ('Hollywood', 'हॉलीवुड', 'Hollywood'), 
        ('Technology', 'टेक्नोलॉजी', 'technology'), ('Market', 'मार्केट भाव', 'market'),
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
    show_in_highlights = models.BooleanField(default=False, verbose_name="Top 5 Highlights?")
    meta_keywords = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'mynews_news'

    def get_absolute_url(self):
        city = self.url_city if self.url_city else "news"
        return reverse('news_detail', kwargs={'url_city': city, 'slug': self.slug})

    @property
    def get_image_url(self):
        if self.image_url:
            return self.image_url
        return "/static/default.png"

# --- Niche wala save method poora replace kar dein ---
    def save(self, *args, **kwargs):
        # 1. District Sync & Slug Logic
        if self.district:
            for eng, hin, city_slug in self.LOCATION_DATA:
                if self.district == eng:
                    self.url_city = eng.lower()
                    self.category = hin
                    break

        if not self.slug:
            latin_title = unidecode(self.title)
            clean_text = latin_title.replace('ii', 'i').replace('ss', 's').replace('aa', 'a').replace('ee', 'e')
            self.slug = f"{slugify(clean_text)[:60]}-{str(uuid.uuid4())[:6]}"

        # 2. Safe Image Processing
        if self.image and hasattr(self.image, 'file'):
            try:
                with Image.open(self.image) as img:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # Thumbnail for speed
                    img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)

                    # --- WATERMARK PATH FIX ---
                    # Aapke bataye gaye raste ke hisaab se:
                    watermark_path = os.path.join(settings.BASE_DIR, 'mynews', 'static', 'watermark.png')
                    
                    if os.path.exists(watermark_path):
                        with Image.open(watermark_path).convert("RGBA") as watermark:
                            base_side = min(img.width, img.height)
                            target_width = int(base_side * 0.20)
                            w_ratio = target_width / float(watermark.size[0])
                            target_height = int(float(watermark.size[1]) * float(w_ratio))
                            watermark = watermark.resize((target_width, target_height), Image.Resampling.LANCZOS)
                            
                            position = (img.width - target_width - 20, img.height - target_height - 20)
                            img.paste(watermark, position, watermark)
                    else:
                        print(f"Watermark not found at: {watermark_path}")

                    # Convert to WEBP
                    output = io.BytesIO()
                    img.save(output, format='WEBP', quality=75)
                    output.seek(0)
                    
                    temp_file = ContentFile(output.read(), name=f"{uuid.uuid4().hex[:10]}.webp")
                    
                    # ImgBB Upload
                    try:
                        uploaded_link = upload_to_imgbb(temp_file)
                        if uploaded_link:
                            self.image_url = uploaded_link
                            # Note: self.image = None yahan nahi karenge, 
                            # varna 500 error ka risk rehta hai.
                    except Exception as upload_err:
                        print(f"ImgBB Error: {upload_err}")
                    
                    output.close()
            except Exception as e:
                print(f"General Image Error: {e}")

        # 3. Final Save to Database
        super().save(*args, **kwargs)
        gc.collect()

    def __str__(self):
        return self.title
