import uuid, io, os, gc, requests
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
    status = models.CharField(max_length=20, choices=[('Draft', 'Draft'), ('Published', 'Published')], default='Published')
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
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Share to FB?")
    is_fb_posted = models.BooleanField(default=False)

    class Meta:
        db_table = 'mynews_news'

    def get_absolute_url(self):
        city = self.url_city if self.url_city else "news"
        return reverse('news_detail', kwargs={'url_city': city, 'slug': self.slug})

    def save(self, *args, **kwargs):
        # 1. जिला और स्लग
        if self.district:
            for eng, hin, city_slug in self.LOCATION_DATA:
                if self.district == eng:
                    self.url_city = eng.lower()
                    self.category = hin
                    break
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))[:60]}-{str(uuid.uuid4())[:6]}"

        # 2. बेसिक डेटा सेव
        super(News, self).save(*args, **kwargs)

        # 3. इमेज प्रोसेसिंग और ImgBB अपलोड
        if self.image and not self.image_url:
            try:
                img = Image.open(self.image)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.thumbnail((1200, 1200))

                # वॉटरमार्क
                try:
                    w_path = os.path.join(settings.BASE_DIR, 'mynews', 'static', 'watermark.png')
                    if os.path.exists(w_path):
                        with Image.open(w_path).convert("RGBA") as w_img:
                            w_img.thumbnail((img.width // 4, img.height // 4))
                            img.paste(w_img, (img.width - w_img.width - 20, img.height - w_img.height - 20), w_img)
                except: pass

                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85)
                output.seek(0)
                
                # --- ImgBB Upload Line ---
                temp_file = ContentFile(output.read(), name=f"{self.slug}.jpg")
                uploaded_link = upload_to_imgbb(temp_file)
                
                if uploaded_link:
                    News.objects.filter(id=self.id).update(image_url=uploaded_link)
                    self.image_url = uploaded_link
                
                img.close()
                output.close()
            except Exception as e:
                print(f"Image Error: {e}")

        # 4. Facebook Share
        if self.share_now_to_fb and not self.is_fb_posted:
            try:
                fb_url = f"https://graph.facebook.com/{settings.FB_PAGE_ID}/feed"
                news_link = f"https://uttarworld.com{self.get_absolute_url()}"
                msg = f"{self.title}\n\nपूरी खबर पढ़ें: {news_link}"
                
                payload = {
                    'message': msg,
                    'access_token': settings.FB_ACCESS_TOKEN
                }
                if self.image_url:
                    payload['link'] = self.image_url
                
                res = requests.post(fb_url, data=payload)
                if res.status_code == 200:
                    News.objects.filter(id=self.id).update(is_fb_posted=True)
            except Exception as e:
                print(f"FB Error: {e}")
        
        gc.collect()

    def __str__(self):
        return self.title
