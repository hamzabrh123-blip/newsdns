import uuid, io, re
import facebook
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

class News(models.Model):
    # Aapne jaisa kaha: 'UP' hata kar har jagah District ka naam English mein kar diya hai
    LOCATION_DATA = [
        ('Agra', 'आगरा', 'Agra'), ('Aligarh', 'अलीगढ़', 'Aligarh'), ('Ambedkar-Nagar', 'अम्बेडकर नगर', 'Ambedkar-Nagar'), 
        ('Amethi', 'अमेठी', 'Amethi'), ('Amroha', 'अमरोहा', 'Amroha'), ('Auraiya', 'औरैया', 'Auraiya'), 
        ('Ayodhya', 'अयोध्या', 'Ayodhya'), ('Azamgarh', 'आजमगढ़', 'Azamgarh'), ('Baghpat', 'बागपत', 'Baghpat'), 
        ('Bahraich', 'बहराइच', 'Bahraich'), ('Ballia', 'बलिया', 'Ballia'), ('Balrampur', 'बालरामपुर', 'Balrampur'), 
        ('Banda', 'बांदा', 'Banda'), ('Barabanki', 'बाराबंकी', 'Barabanki'), ('Bareilly', 'बरेली', 'Bareilly'), 
        ('Basti', 'बस्ती', 'Basti'), ('Bhadohi', 'भदोही', 'Bhadohi'), ('Bijnor', 'बिजनौर', 'Bijnor'), 
        ('Budaun', 'बदायूँ', 'Budaun'), ('Bulandshahr', 'बुलंदशहर', 'Bulandshahr'), ('Chandauli', 'चंदौली', 'Chandauli'), 
        ('Chitrakoot', 'चित्रकूट', 'Chitrakoot'), ('Deoria', 'देवरिया', 'Deoria'), ('Etah', 'एटा', 'Etah'), 
        ('Etawah', 'इटावा', 'Etawah'), ('Farrukhabad', 'फर्रुखाबाद', 'Farrukhabad'), ('Fatehpur', 'फतेहपुर', 'Fatehpur'), 
        ('Firozabad', 'फिरोजाबाद', 'Firozabad'), ('Gautam-Buddha-Nagar', 'नोएडा', 'Gautam-Buddha-Nagar'), 
        ('Ghaziabad', 'गाजियाबाद', 'Ghaziabad'), ('Ghazipur', 'गाजीपुर', 'Ghazipur'), ('Gonda', 'गोंडा', 'Gonda'), 
        ('Gorakhpur', 'गोरखपुर', 'Gorakhpur'), ('Hamirpur', 'हमीरपुर', 'Hamirpur'), ('Hapur', 'हापुड़', 'Hapur'), 
        ('Hardoi', 'हरदोई', 'Hardoi'), ('Hathras', 'हाथरास', 'Hathras'), ('Jalaun', 'जालौन', 'Jalaun'), 
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
        return reverse('news_detail', kwargs={'url_city': city, 'slug': self.slug})

    @property
    def get_image_url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return "/static/default.png"

    def save(self, *args, **kwargs):
        # 1. Logic for Districts & Special Categories
        target_field = self.district if self.district else self.category
        
        if target_field:
            found = False
            for eng, hin, cat in self.LOCATION_DATA:
                if target_field == eng or target_field == hin:
                    self.url_city = eng.lower()
                    # Badge ke liye: आगरा (AGRA) format
                    self.category = f"{hin} ({eng.upper()})"
                    found = True
                    break
            
            if not found:
                self.url_city = slugify(target_field)
        
        # 2. Image Processing
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.thumbnail((1200, 1200), Image.LANCZOS)

                watermark_path = finders.find('watermark.png')
                if watermark_path:
                    watermark = Image.open(watermark_path).convert("RGBA")
                    base_side = min(img.width, img.height)
                    target_width = int(base_side * 0.20) 
                    w_ratio = target_width / float(watermark.size[0])
                    target_height = int(float(watermark.size[1]) * float(w_ratio))
                    watermark = watermark.resize((target_width, target_height), Image.LANCZOS)
                    position = (img.width - target_width - 20, img.height - target_height - 20)
                    img.paste(watermark, position, watermark)

                output = io.BytesIO()
                img.save(output, format='WEBP', quality=50)
                output.seek(0)
                self.image = ContentFile(output.read(), name=f"{uuid.uuid4().hex[:10]}.webp")
                
                uploaded_link = upload_to_imgbb(self.image)
                if uploaded_link:
                    self.image_url = uploaded_link
            except Exception as e:
                print(f"Bhai Image Error: {e}")

        # 3. Slug Logic
        if not self.slug:
            latin_title = unidecode(self.title)
            clean_text = latin_title.replace('ii', 'i').replace('ss', 's').replace('aa', 'a').replace('ee', 'e')
            self.slug = f"{slugify(clean_text)[:60]}-{str(uuid.uuid4())[:6]}"

        super().save(*args, **kwargs)
        
        # 4. Facebook Logic
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            self.post_to_facebook()

    def post_to_facebook(self):
        try:
            if not settings.FB_ACCESS_TOKEN: return
            graph = facebook.GraphAPI(access_token=settings.FB_ACCESS_TOKEN)
            post_url = f"https://uttarworld.com{self.get_absolute_url()}"
            msg = f"🔴 {self.title}\n\nखबर यहाँ पढ़ें: {post_url}"
            
            if self.image_url:
                graph.put_object(parent_object=settings.FB_PAGE_ID, connection_name='photos', url=self.image_url, caption=msg)
            else:
                graph.put_object(parent_object=settings.FB_PAGE_ID, connection_name='feed', message=msg, link=post_url)
            
            News.objects.filter(pk=self.pk).update(is_fb_posted=True, share_now_to_fb=False)
        except Exception as e:
            print(f"FB Error: {e}")

    def __str__(self):
        return self.title
