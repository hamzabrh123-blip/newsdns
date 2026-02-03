import uuid
import facebook
from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from django.urls import reverse
from django.conf import settings
from .utils import upload_to_imgbb 

class News(models.Model):
    # UP ke 75 Districts ki List
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
        ('Firozabad', 'फिरोजाबाद'), ('Gautam-B-Nagar', 'नोएडा/G.B. Nagar'), 
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
    
    # Facebook Fields
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Facebook par post karein?")
    is_fb_posted = models.BooleanField(default=False, verbose_name="Kya FB par post ho chuki hai?")

    def get_absolute_url(self):
        return reverse('news_detail', kwargs={'url_city': self.url_city, 'slug': self.slug})

    def save(self, *args, **kwargs):
        # 1. ImgBB Upload Logic
        if self.image:
            try:
                uploaded_link = upload_to_imgbb(self.image)
                if uploaded_link:
                    self.image_url = uploaded_link
                    # Note: self.image ko None nahi kar rahe taaki admin mein file dikhe
            except Exception as e:
                print(f"ImgBB Error: {e}")

        # 2. URL City Logic
        if not self.url_city:
            self.url_city = slugify(unidecode(self.district)) if self.district else "news"
        else:
            self.url_city = slugify(unidecode(self.url_city))

        # 3. Slug Logic
        if not self.slug:
            self.slug = f"{slugify(unidecode(self.title))}-{str(uuid.uuid4())[:8]}"

        # Database mein save karein
        super().save(*args, **kwargs)

        # 4. FB Share Logic (Sirf tab jab tick ho aur pehle post na hui ho)
        if self.share_now_to_fb and not self.is_fb_posted:
            self.post_to_facebook()

    def post_to_facebook(self):
        """Facebook API Logic"""
        try:
            # --- Inhe replace karein ---
            PAGE_ACCESS_TOKEN = "YOUR_PAGE_ACCESS_TOKEN"
            PAGE_ID = "YOUR_PAGE_ID"
            
            graph = facebook.GraphAPI(access_token=PAGE_ACCESS_TOKEN)
            
            # Website Link
            post_url = f"https://uttarworld.com{self.get_absolute_url()}"
            message = f"🔴 {self.title}\n\nपूरी खबर यहाँ पढ़ें: {post_url}\n\n#UttarWorld #News #UPNews"

            # Image ke saath post
            if self.image_url:
                graph.put_object(
                    parent_object=PAGE_ID,
                    connection_name='photos',
                    url=self.image_url,
                    caption=message
                )
            else:
                graph.put_object(
                    parent_object=PAGE_ID,
                    connection_name='feed',
                    message=message,
                    link=post_url
                )

            # Update flags after success (using update to avoid recursion)
            News.objects.filter(pk=self.pk).update(is_fb_posted=True, share_now_to_fb=False)
            print("FB Post Successful!")
            
        except Exception as e:
            print(f"Facebook API Error: {e}")

    def __str__(self):
        return self.title