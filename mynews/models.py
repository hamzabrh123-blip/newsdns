import uuid, io, re
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
    LOCATION_DATA = [
        ('Agra', 'आगरा', 'UP'), ('Aligarh', 'अलीगढ़', 'UP'), ('Ambedkar-Nagar', 'अम्बेडकर नगर', 'UP'), 
        ('Amethi', 'अमेठी', 'UP'), ('Amroha', 'अमरोहा', 'UP'), ('Auraiya', 'औरैया', 'UP'), 
        ('Ayodhya', 'अयोध्या', 'UP'), ('Azamgarh', 'आजमगढ़', 'UP'), ('Baghpat', 'बागपत', 'UP'), 
        ('Bahraich', 'बहराइच', 'UP'), ('Ballia', 'बलिया', 'UP'), ('Balrampur', 'बालरामपुर', 'UP'), 
        ('Banda', 'बांदा', 'UP'), ('Barabanki', 'बाराबंकी', 'UP'), ('Bareilly', 'बरेली', 'UP'), 
        ('Basti', 'बस्ती', 'UP'), ('Bhadohi', 'भदोही', 'UP'), ('Bijnor', 'बिजनौर', 'UP'), 
        ('Budaun', 'बदायूँ', 'UP'), ('Bulandshahr', 'बुलंदशहर', 'UP'), ('Chandauli', 'चंदौली', 'UP'), 
        ('Chitrakoot', 'चित्रकूट', 'UP'), ('Deoria', 'देवरिया', 'UP'), ('Etah', 'एटा', 'UP'), 
        ('Etawah', 'इटावा', 'UP'), ('Farrukhabad', 'फर्रुखाबाद', 'UP'), ('Fatehpur', 'फतेहपुर', 'UP'), 
        ('Firozabad', 'फिरोजाबाद', 'UP'), ('Gautam-Buddha-Nagar', 'नोएडा', 'UP'), 
        ('Ghaziabad', 'गाजियाबाद', 'UP'), ('Ghazipur', 'गाजीपुर', 'UP'), ('Gonda', 'गोंडा', 'UP'), 
        ('Gorakhpur', 'गोरखपुर', 'UP'), ('Hamirpur', 'हमीरपुर', 'UP'), ('Hapur', 'हापुड़', 'UP'), 
        ('Hardoi', 'हरदोई', 'UP'), ('Hathras', 'हाथरास', 'UP'), ('Jalaun', 'जालौन', 'UP'), 
        ('Jaunpur', 'जाँयपुर', 'UP'), ('Jhansi', 'झाँसी', 'UP'), ('Kannauj', 'कन्नौज', 'UP'), 
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
        db_table = 'mynews_news_v6'  # Ye line Supabase mein fresh table banayegi aur error khatam karegi

    def get_absolute_url(self):
        city = self.url_city if self.url_city else "news"
        return reverse('news_detail', kwargs={'url_city': city, 'slug': self.slug})

    @property
    def get_image_url(self):
        if self.image_url:
            return self.image_url
        return "/static/default.png"

    def save(self, *args, **kwargs):
        if self.district:
            for eng, hin, cat in self.LOCATION_DATA:
                if self.district == eng:
                    self.url_city = eng.lower()
                    self.category = cat
                    break

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
                    self.image = None
            except Exception as e:
                print(f"Bhai Error: {e}")

        if not self.slug:
            latin_title = unidecode(self.title)
            clean_text = latin_title.replace('ii', 'i').replace('ss', 's').replace('aa', 'a').replace('ee', 'e')
            self.slug = f"{slugify(clean_text)[:60]}-{str(uuid.uuid4())[:6]}"

        super().save(*args, **kwargs)
        
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            self.post_to_facebook()

    def post_to_facebook(self):
        try:
            import facebook
            graph = facebook.GraphAPI(access_token=settings.FB_ACCESS_TOKEN)
            post_url = f"https://uttarworld.com{self.get_absolute_url()}"
            msg = f"🔴 {self.title}\n\nखबर यहाँ पढ़ें: {post_url}"
            if self.image_url:
                graph.put_object(parent_object=settings.FB_PAGE_ID, connection_name='photos', url=self.image_url, caption=msg)
            News.objects.filter(pk=self.pk).update(is_fb_posted=True, share_now_to_fb=False)
        except Exception as e:
            print(f"FB Error: {e}")

    def __str__(self):
        return self.title
