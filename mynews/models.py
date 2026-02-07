import uuid, io
from PIL import Image
from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from django.urls import reverse
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.staticfiles import finders
from .utils import upload_to_imgbb 

# Facebook logic safe rakhein
try:
    import facebook
except ImportError:
    facebook = None

class News(models.Model):
    LOCATION_DATA = [
        ('Agra', 'आगरा', 'Agra'), ('Aligarh', 'अलीगढ़', 'Aligarh'), ('Ambedkar-Nagar', 'अम्बेडकर नगर', 'Ambedkar-Nagar'), 
        ('Amethi', 'अमेठी', 'Amethi'), ('Amroha', 'अमरोहा', 'Amroha'), ('Auraiya', 'औरैया', 'Auraiya'), 
        ('Ayodhya', 'अयोध्या', 'Ayodhya'), ('Azamgarh', 'आजमगढ़', 'Azamgarh'), ('Baghpat', 'बागपत', 'Baghpat'), 
        ('Bahraich', 'बहराइच', 'Bahraich'), ('Ballia', 'बलिया', 'Ballia'), ('Balrampur', 'बालरामपुर', 'Balrampur'), 
        ('Banda', 'बांदा', 'Banda'), ('Barabanki', 'बाराबंकी', 'Barabanki'), ('Bareilly', 'बरेली', 'Bareilly'), 
        ('Basti', 'बस्ती', 'Basti'), ('Bhadohi', 'भदोही', 'Bhadohi'), ('Bijnor', 'बिजनौर', 'Bijnor'), 
        ('Budaun', 'बदायूँ', 'Budaun'), ('Bulandshahr', 'बुलंदशहर', 'Bulandshahr'), ('Chandauli', 'चंदौली', 'Chandauli'), 
        ('Chitrakoot', 'चित्रकूट', 'Chitrakoot'), ('Deoria', 'देवरिया', 'Deoria'), ('Etah', 'एटा', 'Etah'), 
        ('Etawah', 'इटावा', 'Etawah'), ('Farrukhabad', 'फर्रुखाबाद', 'Farrukhabad'), ('Fatehpur', 'फतेहpur', 'Fatehpur'), 
        ('Firozabad', 'फिरोजाबाद', 'Firozabad'), ('Gautam-Buddha-Nagar', 'नोएडा', 'Gautam-Buddha-Nagar'), 
        ('Ghaziabad', 'गाजियाबाद', 'Ghaziabad'), ('Ghazipur', 'गाजीपुर', 'Ghazipur'), ('Gonda', 'गोंडा', 'Gonda'), 
        ('Gorakhpur', 'गोरखपुर', 'Gorakhpur'), ('Hamirpur', 'हमीरपुर', 'Hamirpur'), ('Hapur', 'हापुड़', 'Hapur'), 
        ('Hardoi', 'हरदोई', 'Hardoi'), ('Hathras', 'हाथराas', 'Hathras'), ('Jalaun', 'जालौन', 'Jalaun'), 
        ('Jaunpur', 'जाँयपुर', 'Jaunpur'), ('Jhansi', 'झाँसी', 'Jhansi'), ('Kannauj', 'कन्नौज', 'Kannauj'), 
        ('Kanpur-Dehat', 'कानपुर देहात', 'Kanpur-Dehat'), ('Kanpur-Nagar', 'कानपुर नगर', 'Kanpur-Nagar'), 
        ('Kasganj', 'कासगंज', 'Kasganj'), ('Kaushambi', 'कौशाम्बी', 'Kaushambi'), ('Kushinagar', 'कुशीनगर', 'Kushinagar'), 
        ('Lakhimpur-Kheri', 'लखीमपुर खीरी', 'Lakhimpur-Kheri'), ('Lalitpur', 'ललितपुर', 'Lalitpur'), 
        ('Lucknow', 'लखनऊ', 'Lucknow'), ('Maharajganj', 'महराजगंज', 'Maharajganj'), ('Mahoba', 'महोबा', 'Mahoba'), 
        ('Mainpuri', 'मैनपुरी', 'Mainpuri'), ('Mathura', 'मथुरा', 'Mathura'), ('Mau', 'मऊ', 'Mau'), 
        ('Meerut', 'मेरठ', 'Meerut'), ('Mirzapur', 'मिर्जापुर', 'Mirzapur'), ('Moradabad', 'मुरादाबाद', 'Moradabad'), 
        ('Muzaffarnagar', 'मुजफ्फरनगर', 'Muzaffarnagar'), ('Pilibhit', 'पीलीभीत', 'Pilibhit'), ('Pratapgarh', 'प्रतापगढ़', 'Pratapgarh'), 
        ('Prayagraj', 'प्रयागराज', 'Prayagraj'), ('Rae-Bareli', 'रायबरेली', 'Rae-Bareli'), ('Rampur', 'रामपुर', 'Rampur'), 
        ('Saharanpur', 'सहारनपुर', 'Saharanpur'), ('Sambhal', 'सम्भल', 'Sambhal'), ('Sant-Kabir-Nagar', 'संत कबीर नगर', 'Sant-Kabir-Nagar'), 
        ('Shahjahanpur', 'शाहजहांपुर', 'Shahjahanpur'), ('Shamli', 'शामली', 'Shamli'), ('Shravasti', 'श्रावस्ती', 'Shravasti'), 
        ('Siddharthnagar', 'सिद्धार्थनगर', 'Siddharthnagar'), ('Sitapur', 'सीतापुर', 'Sitapur'), ('Sonbhadra', 'सोनभद्र', 'Sonbhadra'), 
        ('Sultanpur', 'सुलतानपुर', 'Sultanpur'), ('Unnao', 'उन्नाव', 'Unnao'), ('Varanasi', 'वाराणसी', 'Varanasi'),
        ('Delhi', 'दिल्ली', 'National'), ('National', 'राष्ट्रीय खबर', 'National'),
        ('International', 'अंतर्राष्ट्रीय', 'International'), ('Sports', 'खेल समाचार', 'Sports'),
        ('Bollywood', 'बॉलीवुड', 'Entertainment'), ('Technology', 'टेक्नोलॉजी', 'Technology'), 
        ('Market', 'मार्केट भाव', 'Market'),
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
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Facebook post?")
    is_fb_posted = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False, verbose_name="Breaking News?")
    meta_keywords = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'mynews_news'

    def get_absolute_url(self):
        city = self.url_city if self.url_city else "news"
        return f"/{city}/{self.slug}/"

    def save(self, *args, **kwargs):
        # 1. TECHNOLOGY & CATEGORY LOGIC
        # Priority 1: Check if District is selected
        if self.district:
            for eng, hin, cat_val in self.LOCATION_DATA:
                if self.district == eng:
                    self.url_city = eng.lower()
                    self.category = f"{hin} ({eng.upper()})"
                    break
        # Priority 2: Check if Category is Technology or others
        elif self.category:
            cat_clean = self.category.lower().strip()
            if 'technology' in cat_clean or 'टेक्नोलॉजी' in cat_clean:
                self.url_city = 'technology'
                self.category = 'टेक्नोलॉजी (TECHNOLOGY)'
            else:
                for eng, hin, cat_val in self.LOCATION_DATA:
                    if self.category == eng or self.category == hin:
                        self.url_city = eng.lower()
                        self.category = f"{hin} ({eng.upper()})"
                        break
        
        if not self.url_city:
            self.url_city = "news"

        # 2. SLUG LOGIC
        if not self.slug:
            self.slug = f"{slugify(unidecode(str(self.title)))[:60]}-{str(uuid.uuid4())[:6]}"

        # 3. IMAGE PROCESSING (Total Safe)
        if self.image and hasattr(self.image, 'file') and not self.image_url:
            try:
                img = Image.open(self.image)
                if img.mode != 'RGB': img = img.convert('RGB')
                img.thumbnail((1200, 1200), Image.LANCZOS)
                output = io.BytesIO()
                img.save(output, format='WEBP', quality=60)
                output.seek(0)
                self.image = ContentFile(output.read(), name=f"{uuid.uuid4().hex[:10]}.webp")
                
                # ImgBB Upload
                try:
                    up_link = upload_to_imgbb(self.image)
                    if up_link: self.image_url = up_link
                except: pass
            except: pass

        # SABSE PEHLE SAVE (TAAKI 500 NA AAYE)
        super().save(*args, **kwargs)
        
        # 4. FACEBOOK (AFTER SAVE)
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            try:
                self.post_to_facebook()
            except:
                pass

    def post_to_facebook(self):
        if not facebook or not hasattr(settings, 'FB_ACCESS_TOKEN') or not settings.FB_ACCESS_TOKEN:
            return
        try:
            graph = facebook.GraphAPI(access_token=settings.FB_ACCESS_TOKEN)
            post_url = f"https://uttarworld.com/{self.url_city}/{self.slug}/"
            msg = f"🔴 {self.title}\n\nपूरी खबर यहाँ पढ़ें: {post_url}"
            
            if self.image_url:
                graph.put_object(parent_object=settings.FB_PAGE_ID, connection_name='photos', url=self.image_url, caption=msg)
            else:
                graph.put_object(parent_object=settings.FB_PAGE_ID, connection_name='feed', message=msg, link=post_url)
            
            # Direct update taaki save loop na bane
            self.__class__.objects.filter(pk=self.pk).update(is_fb_posted=True, share_now_to_fb=False)
        except:
            pass

    def __str__(self):
        return self.title
