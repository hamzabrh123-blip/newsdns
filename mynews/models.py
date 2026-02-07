import uuid
from django.db import models
from ckeditor.fields import RichTextField 
from django.utils.text import slugify
from django.utils.timezone import now
from unidecode import unidecode

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
    is_important = models.BooleanField(default=False, verbose_name="Breaking News?")
    meta_keywords = models.TextField(blank=True, null=True)

    # --- FB Automation Fields (Dhakka lagane ke liye zaroori) ---
    share_now_to_fb = models.BooleanField(default=False, verbose_name="Facebook post?")
    is_fb_posted = models.BooleanField(default=False)

    class Meta:
        db_table = 'mynews_news'

    def save(self, *args, **kwargs):
        # 1. TECHNOLOGY FIX
        is_tech = False
        if self.category:
            c_val = str(self.category).lower()
            if 'technology' in c_val or 'टेक्नोलॉजी' in c_val:
                self.url_city = 'technology'
                self.category = 'टेक्नोलॉजी (TECHNOLOGY)'
                is_tech = True
        
        # 2. DISTRICT LOGIC
        if not is_tech and self.district:
            for eng, hin, cat_v in self.LOCATION_DATA:
                if self.district == eng:
                    self.url_city = eng.lower()
                    self.category = f"{hin} ({eng.upper()})"
                    break
        
        # Default City
        if not self.url_city:
            self.url_city = "news"

        # 3. SLUG LOGIC
        if not self.slug:
            self.slug = f"{slugify(unidecode(str(self.title)))[:60]}-{str(uuid.uuid4())[:6]}"

        # 4. FINAL SAVE
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
