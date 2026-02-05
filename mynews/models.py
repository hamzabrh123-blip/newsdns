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
    UP_CITIES = [
        ('Agra', 'आगरा'), ('Aligarh', 'अलीगढ़'), ('Ambedkar-Nagar', 'अम्बेडकर नगर'), 
        ('Amethi', 'अमेठी'), ('Amroha', 'अमरोha'), ('Auraiya', 'औरैया'), 
        ('Ayodhya', 'अयोध्या'), ('Azamgarh', 'आजमगढ़'), ('Baghpat', 'बागपत'), 
        ('Bahraich', 'बहराइच'), ('Ballia', 'बलिया'), ('Balrampur', 'बलरामपुर'), 
        ('Banda', 'बांदा'), ('Barabanki', 'बाराबंकी'), ('Bareilly', 'बरेली'), 
        ('Basti', 'बस्ती'), ('Bhadohi', 'भदोही'), ('Bijnor', 'बिजनौर'), 
        ('Budaun', 'बदायूँ'), ('Bulandshahr', 'बुलंदशहर'), ('Chandauli', 'चंदौली'), 
        ('Chitrakoot', 'चित्रकूट'), ('Deoria', 'देवरिया'), ('Etah', 'एटा'), 
        ('Etawah', 'इटावा'), ('Farrukhabad', 'फर्रुखाबाद'), ('Fatehpur', 'फतेहपुर'), 
        ('Firozabad', 'फिरोजाबाद'), ('Noida', 'नोएडा'), # <--- Yahan Noida sahi kar diya
        ('Ghaziabad', 'गाजियाबाद'), ('Ghazipur', 'गाजीपुर'), ('Gonda', 'गोंडा'), 
        ('Gorakhpur', 'गोरखपुर'), ('Hamirpur', 'हमीरपुर'), ('Hapur', 'हापुड़'), 
        ('Hardoi', 'हरदोई'), ('Hathras', 'हाथराas'), ('Jalaun', 'जालौन'), 
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
    ]

    OTHER_CHOICES = [
        ('Int-MiddleEast', 'मिडिल ईस्ट'), ('Int-America', 'अमेरिका'),
        ('International', 'अंतर्राष्ट्रीय'), ('Sports', 'खेल'),
        ('Bollywood', 'बॉलीवुड'), ('Technology', 'टेक्नोलॉजी'),
        ('Market', 'मार्केट'), ('Other-States', 'अन्य राज्य'),
        ('UP-National', 'यूपी राष्ट्रीय'), ('National', 'राष्ट्रीय'),
    ]

    LOCATION_CHOICES = OTHER_CHOICES + UP_CITIES

    title = models.CharField(max_length=250)
    category = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, choices=LOCATION_CHOICES, blank=True, null=True)
    url_city = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(default=now)
    content = RichTextField(blank=True) 
    image = models.ImageField("Upload Image", upload_to="news_pics/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    is_important = models.BooleanField(default=False, verbose_name="Breaking News?")
    meta_keywords = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Facebook par post karein?")
    is_fb_posted = models.BooleanField(default=False, verbose_name="Kya FB par post ho chuki hai?")

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'url_city': self.url_city, 'slug': self.slug})

    def save(self, *args, **kwargs):
        # --- IMAGE COMPRESSION TO WEBP (30-50KB) ---
        if self.image:
            try:
                img = Image.open(self.image)
                img.thumbnail((1000, 1000), Image.LANCZOS)
                
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                output = io.BytesIO()
                img.save(output, format='WEBP', quality=40, optimize=True)
                output.seek(0)

                new_filename = f"{slugify(unidecode(self.title))[:30]}.webp"
                self.image = ContentFile(output.read(), name=new_filename)

                # --- IMGBB UPLOAD ---
                uploaded_link = upload_to_imgbb(self.image)
                if uploaded_link:
                    self.image_url = uploaded_link
                    self.image = None 
            except Exception as e:
                print(f"Image Magic Error: {e}")

        # --- AUTO URL_CITY FROM DROPDOWN ---
        if self.district:
            # Ab Noida select karne par url_city 'noida' banegi
            self.url_city = slugify(unidecode(self.district))
        
        if not self.url_city:
            self.url_city = "news"

        # --- AUTO SLUG ---
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))}-{str(uuid.uuid4())[:8]}"

        super().save(*args, **kwargs)

        if self.share_now_to_fb and not self.is_fb_posted:
            self.post_to_facebook()

    def post_to_facebook(self):
        try:
            PAGE_ACCESS_TOKEN = getattr(settings, "FB_ACCESS_TOKEN", None)
            PAGE_ID = getattr(settings, "FB_PAGE_ID", None)
            
            if not PAGE_ACCESS_TOKEN or not PAGE_ID:
                return

            graph = facebook.GraphAPI(access_token=PAGE_ACCESS_TOKEN)
            post_url = f"https://uttarworld.com{self.get_absolute_url()}"
            message = f"🔴 {self.title}\n\nपूरी खबर यहाँ पढ़ें: {post_url}"
            
            if self.image_url:
                graph.put_object(parent_object=PAGE_ID, connection_name='photos', url=self.image_url, caption=message)
            else:
                graph.put_object(parent_object=PAGE_ID, connection_name='feed', message=message, link=post_url)
            
            self.__class__.objects.filter(pk=self.pk).update(is_fb_posted=True, share_now_to_fb=False)
        except Exception as e:
            print(f"Facebook API Error: {e}")

    def __str__(self):
        return self.title
