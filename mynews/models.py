import uuid
import facebook
import io
from PIL import Image
from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from django.urls import reverse
from django.conf import settings
from django.core.files.base import ContentFile
from .utils import upload_to_imgbb 

class News(models.Model):
    # --- Sab Kuch Ek Hi List Mein (English, Hindi, Category) ---
    LOCATION_DATA = [
        # UP Districts (75)
        ('Agra', 'आगरा', 'UP'), ('Aligarh', 'अलीगढ़', 'UP'), ('Ambedkar-Nagar', 'अम्बेडकर नगर', 'UP'), 
        ('Amethi', 'अमेठी', 'UP'), ('Amroha', 'अमरोहा', 'UP'), ('Auraiya', 'औरैया', 'UP'), 
        ('Ayodhya', 'अयोध्या', 'UP'), ('Azamgarh', 'आजमgarh', 'UP'), ('Baghpat', 'बागपत', 'UP'), 
        ('Bahraich', 'बहराइच', 'UP'), ('Ballia', 'बलिया', 'UP'), ('Balrampur', 'बलरामपुर', 'UP'), 
        ('Banda', 'बांदा', 'UP'), ('Barabanki', 'बाराबंकी', 'UP'), ('Bareilly', 'बरेली', 'UP'), 
        ('Basti', 'बस्ती', 'UP'), ('Bhadohi', 'भदोही', 'UP'), ('Bijnor', 'बिजनौर', 'UP'), 
        ('Budaun', 'बदायूँ', 'UP'), ('Bulandshahr', 'बुलंदशहर', 'UP'), ('Chandauli', 'चंदौली', 'UP'), 
        ('Chitrakoot', 'चित्रकूट', 'UP'), ('Deoria', 'देवरिया', 'UP'), ('Etah', 'एटा', 'UP'), 
        ('Etawah', 'इटावा', 'UP'), ('Farrukhabad', 'फर्रुखाबाद', 'UP'), ('Fatehpur', 'फतेहपुर', 'UP'), 
        ('Firozabad', 'फिरोजाबाद', 'UP'), ('Gautam-Buddha-Nagar', 'नोएडा', 'UP'), 
        ('Ghaziabad', 'गाजियाबाद', 'UP'), ('Ghazipur', 'गाजीपुर', 'UP'), ('Gonda', 'गोंडा', 'UP'), 
        ('Gorakhpur', 'गोरखपुर', 'UP'), ('Hamirpur', 'हमीरपुर', 'UP'), ('Hapur', 'हापुड़', 'UP'), 
        ('Hardoi', 'हरदोई', 'UP'), ('Hathras', 'हाथरास', 'UP'), ('Jalaun', 'जालौन', 'UP'), 
        ('Jaunpur', 'जौनपुर', 'UP'), ('Jhansi', 'झाँसी', 'UP'), ('Kannauj', 'कन्नौज', 'UP'), 
        ('Kanpur-Dehat', 'कानपुर देहात', 'UP'), ('Kanpur-Nagar', 'कानपुर नगर', 'UP'), 
        ('Kasganj', 'कासगंज', 'UP'), ('Kaushambi', 'कौशाम्बी', 'UP'), ('Kushinagar', 'कुशीनगर', 'UP'), 
        ('Lakhimpur-Kheri', 'लखीमपुर खीरी', 'UP'), ('Lalitpur', 'ललितपुर', 'UP'), 
        ('Lucknow', 'लखनऊ', 'UP'), ('Maharajganj', 'महराजगंज', 'UP'), ('Mahoba', 'महोबा', 'UP'), 
        ('Mainpuri', 'मैनपुरी', 'UP'), ('Mathura', 'मथुरा', 'UP'), ('Mau', 'मऊ', 'UP'), 
        ('Meerut', 'मेरठ', 'UP'), ('Mirzapur', 'मिर्जापुर', 'UP'), ('Moradabad', 'मुरादाबाद', 'UP'), 
        ('Muzaffarnagar', 'मुजफ्फरनगर', 'UP'), ('Pilibhit', 'पीलीभीत', 'UP'), ('Pratapgarh', 'प्रतापगढ़', 'UP'), 
        ('Prayagraj', 'प्रयागराज', 'UP'), ('Rae-Bareli', 'रायबरेली', 'UP'), ('Rampur', 'रामपुर', 'UP'), 
        ('Saharanpur', 'सहारनपुर', 'UP'), ('Sambhal', 'सम्भल', 'UP'), ('Sant-Kabir-Nagar', 'संत कबीर नगर', 'UP'), 
        ('Shahjahanpur', 'शाहजहांपुर', 'UP'), ('Shamli', 'शामली', 'UP'), ('Shravasti', 'श्रावस्ती', 'UP'), 
        ('Siddharthnagar', 'सिद्धार्थनगर', 'UP'), ('Sitapur', 'सीतापुर', 'UP'), ('Sonbhadra', 'सोनभद्र', 'UP'), 
        ('Sultanpur', 'सुलतानपुर', 'UP'), ('Unnao', 'उन्नाव', 'UP'), ('Varanasi', 'वाराणसी', 'UP'),
        
        # Categories & Other Cities
        ('Delhi', 'दिल्ली', 'National'), ('National', 'राष्ट्रीय खबर', 'National'),
        ('Int-MiddleEast', 'मिडिल ईस्ट', 'International'), ('Int-America', 'अमेरिका', 'International'),
        ('International', 'अंतर्राष्ट्रीय', 'International'), ('Sports', 'खेल समाचार', 'Sports'),
        ('Bollywood', 'बॉलीवुड', 'Entertainment'), ('Hollywood', 'हॉलीवुड', 'Entertainment'),
        ('Technology', 'टेक्नोलॉजी', 'Technology'), ('Market', 'मार्केट भाव', 'Market'),
    ]

    title = models.CharField(max_length=250)
    # Backend Auto-fill fields
    category = models.CharField(max_length=100, blank=True)
    url_city = models.CharField(max_length=100, blank=True)
    
    # Dropdown Menu
    district = models.CharField(max_length=100, choices=[(x[0], x[1]) for x in LOCATION_DATA])
    
    content = RichTextField(blank=True) 
    image = models.ImageField(upload_to="news_pics/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    date = models.DateTimeField(default=now)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Facebook post?")
    is_fb_posted = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'url_city': self.url_city, 'slug': self.slug})

    def save(self, *args, **kwargs):
        # --- Logic: Auto-populate Category & url_city ---
        for eng, hin, cat in self.LOCATION_DATA:
            if self.district == eng:
                self.url_city = eng.lower() # Link ke liye english
                self.category = cat # Filter ke liye category
                break

        # Image Logic
        if self.image:
            try:
                img = Image.open(self.image)
                img.thumbnail((1000, 1000), Image.LANCZOS)
                output = io.BytesIO()
                img.save(output, format='WEBP', quality=40)
                output.seek(0)
                self.image = ContentFile(output.read(), name=f"{uuid.uuid4().hex[:10]}.webp")
                uploaded_link = upload_to_imgbb(self.image)
                if uploaded_link:
                    self.image_url = uploaded_link
                    self.image = None
            except: pass

        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))[:60]}-{str(uuid.uuid4())[:6]}"

        super().save(*args, **kwargs)
        if self.share_now_to_fb and not self.is_fb_posted:
            self.post_to_facebook()

    def post_to_facebook(self):
        try:
            graph = facebook.GraphAPI(access_token=settings.FB_ACCESS_TOKEN)
            post_url = f"https://uttarworld.com{self.get_absolute_url()}"
            msg = f"🔴 {self.title}\n\nखबर यहाँ पढ़ें: {post_url}"
            if self.image_url:
                graph.put_object(parent_object=settings.FB_PAGE_ID, connection_name='photos', url=self.image_url, caption=msg)
            self.__class__.objects.filter(pk=self.pk).update(is_fb_posted=True, share_now_to_fb=False)
        except: pass

    def __str__(self): return self.title
