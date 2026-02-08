import uuid, io
from PIL import Image
from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode
from django.urls import reverse
from django.core.files.base import ContentFile
from django.contrib.staticfiles import finders
from django.conf import settings  # Facebook settings ke liye
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
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Facebook post?")
    is_fb_posted = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False, verbose_name="Breaking News?")
    
    # --- YAHAN SET KIYA HAI TOP 5 HIGHLIGHTS ---
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

    def save(self, *args, **kwargs):
        # 1. District/Category Sync Logic
        if self.district:
            for eng, hin, city_slug in self.LOCATION_DATA:
                if self.district == eng:
                    self.url_city = eng.lower()
                    self.category = hin # Yahan 'hin' (Hindi naam) save hoga
                    break

        # 2. Image, Watermark and ImgBB Upload
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)

                watermark_path = finders.find('watermark.png')
                if watermark_path:
                    watermark = Image.open(watermark_path).convert("RGBA")
                    base_side = min(img.width, img.height)
                    target_width = int(base_side * 0.20) 
                    w_ratio = target_width / float(watermark.size[0])
                    target_height = int(float(watermark.size[1]) * float(w_ratio))
                    watermark = watermark.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    position = (img.width - target_width - 20, img.height - target_height - 20)
                    img.paste(watermark, position, watermark)
                    watermark.close()

                output = io.BytesIO()
                # WEBP format for better SEO and speed
                img.save(output, format='WEBP', quality=60)
                output.seek(0)
                
                # Temp file to upload
                temp_file = ContentFile(output.read(), name=f"{uuid.uuid4().hex[:10]}.webp")
                uploaded_link = upload_to_imgbb(temp_file)
                
                if uploaded_link:
                    self.image_url = uploaded_link
                    self.image = None # Local storage bachane ke liye
                img.close()
            except Exception as e:
                print(f"Bhai Image Processing Error: {e}")

        # 3. Slug Creation
        if not self.slug:
            latin_title = unidecode(self.title)
            # Clean text for cleaner URLs
            clean_text = latin_title.replace('ii', 'i').replace('ss', 's').replace('aa', 'a').replace('ee', 'e')
            self.slug = f"{slugify(clean_text)[:60]}-{str(uuid.uuid4())[:6]}"

        super().save(*args, **kwargs)
        
     # Facebook control fields
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Facebook par share karein?")
    is_fb_posted = models.BooleanField(default=False, verbose_name="Kya FB par post ho chuki hai?")

    # ... (baaki fields wahi rahengi)

    def save(self, *args, **kwargs):
        # 1. District/Category Sync logic (Wahi rahega)
        if self.district:
            for eng, hin, city_slug in self.LOCATION_DATA:
                if self.district == eng:
                    self.url_city = eng.lower()
                    self.category = hin
                    break

        # 2. Image Processing & ImgBB (Wahi rahega)
        # ... (Image wala poora logic jo tune bheja tha)

        # 3. Slug creation (Wahi rahega)
        if not self.slug:
            latin_title = unidecode(self.title)
            clean_text = latin_title.replace('ii', 'i').replace('ss', 's').replace('aa', 'a').replace('ee', 'e')
            self.slug = f"{slugify(clean_text)[:60]}-{str(uuid.uuid4())[:6]}"

        # --- FACEBOOK SHARE LOGIC ---
        # Pehle news save hogi taaki URL ban jaye
        super().save(*args, **kwargs)
        
        # Agar status Published hai aur humne Tick kiya hai, aur pehle post nahi hui hai
        if self.status == 'Published' and self.share_now_to_fb and not self.is_fb_posted:
            self.post_to_facebook()

    def post_to_facebook(self):
        try:
            import facebook
            # Ye settings.py se token uthayega
            graph = facebook.GraphAPI(access_token=settings.FB_ACCESS_TOKEN)
            
            # Aapki site ka full link
            post_url = f"https://uttarworld.com{self.get_absolute_url()}"
            msg = f"🔴 {self.title}\n\nपूरी खबर यहाँ पढ़ें: {post_url}"
            
            if self.image_url:
                # Photo ke sath post
                graph.put_object(
                    parent_object=settings.FB_PAGE_ID, 
                    connection_name='photos', 
                    url=self.image_url, 
                    caption=msg
                )
            else:
                # Bina photo ke sirf link post
                graph.put_object(
                    parent_object=settings.FB_PAGE_ID, 
                    connection_name='feed', 
                    message=msg, 
                    link=post_url
                )
            
            # Post hone ke baad is_fb_posted ko True kar do taaki baar-baar post na ho
            News.objects.filter(pk=self.pk).update(is_fb_posted=True, share_now_to_fb=False)
            print("FB Post Success!")
            
        except Exception as e:
            print(f"FB Error: {e}")

    def __str__(self):
        return self.title
