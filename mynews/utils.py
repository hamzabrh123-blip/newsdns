import requests
import re
import base64
import os
import logging
import gc
import io
from PIL import Image
import pillow_avif  # AVIF सपोर्ट के लिए ज़रूरी
from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)

# --- 1. SIDEBAR LOGIC ---
def get_common_sidebar_data():
    try:
        # डायनामिक तरीके से मॉडल उठाना ताकि Circular Import न हो
        News = apps.get_model('mynews', 'News') 
        return {
            "bazaar_sidebar": News.objects.filter(category="Market", status='Published').order_by("-date")[:5],
            "bharat_sidebar": News.objects.filter(category="National", status='Published').order_by("-date")[:10],
            "duniya_sidebar": News.objects.filter(category="International", status='Published').order_by("-date")[:10],
            "technology_sidebar": News.objects.filter(category="Technology", status='Published').order_by("-date")[:3],
            "bollywood_sidebar": News.objects.filter(category="Bollywood", status='Published').order_by("-date")[:3],
            "lucknow_up_sidebar": News.objects.filter(district='Lucknow', status='Published').order_by("-date")[:10],
        }
    except Exception as e:
        logger.error(f"Sidebar Data Error: {e}")
        return {}

# --- 2. MASTER IMAGE PROCESSING & IMGBB (Universal Engine) ---
def process_and_upload_to_imgbb(instance):
    """
    यह फंक्शन News (Image 1) और NewsImage (Gallery) दोनों के लिए काम करेगा।
    इसमें वॉटरमार्क लगेगा और फोटो ImgBB पर अपलोड होगी।
    """
    # 1. इमेज फील्ड चेक करें
    image_field = getattr(instance, 'image', None)
    if not image_field:
        return None

    # 2. API Key चेक करें
    api_key = os.environ.get("IMGBB_API_KEY") or "d0528bc96d36a90b0cfbac9227174e41"
    
    try:
        # RAM बचाने के लिए BytesIO का उपयोग
        img_data = image_field.read()
        img = Image.open(io.BytesIO(img_data))

        # AVIF/WebP को RGB में बदलें ताकि वॉटरमार्क लग सके
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        
        # 512MB RAM के लिए साइज कंट्रोल (1000px काफी है)
        img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)

        # --- Watermark Logic (पक्का रास्ता) ---
        try:
            # पहले Django Static से ढूंढो
            w_path = os.path.join(settings.BASE_DIR, 'mynews', 'static', 'watermark.png')
            
            # अगर वहां न मिले तो लोकल PC वाले रास्ते पर देखो
            if not os.path.exists(w_path):
                w_path = r"C:\Users\siraj\uttarworld_project\mynews\static\watermark.png"
            
            if os.path.exists(w_path):
                with Image.open(w_path).convert("RGBA") as w_img:
                    # वॉटरमार्क साइज: मेन इमेज का 18%
                    w_img.thumbnail((img.width // 5, img.height // 5))
                    # Bottom Right पोजीशन
                    pos = (img.width - w_img.width - 20, img.height - w_img.height - 20)
                    img.paste(w_img, pos, w_img)
            else:
                logger.warning(f"Watermark file not found at: {w_path}")
        except Exception as we:
            logger.error(f"Watermark Error: {we}")

        # --- Memory Optimized Saving ---
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        base64_image = base64.b64encode(output.getvalue())

        # भारी डेटा डिलीट करें ताकि RAM खाली हो
        img.close()
        del img_data
        gc.collect()

        # 3. ImgBB पर अपलोड
        payload = {"key": api_key, "image": base64_image}
        response = requests.post("https://api.imgbb.com/1/upload", data=payload, timeout=30)

        if response.status_code == 200:
            return response.json()['data']['url']
        
        logger.error(f"ImgBB Upload Failed: {response.text}")
        return None

    except Exception as e:
        logger.error(f"Image Processing Error: {e}")
        return None
    finally:
        gc.collect()

# --- 3. FACEBOOK AUTO-POST ---
def post_to_facebook(instance):
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_ids = [os.environ.get('FB_PAGE_ID'), os.environ.get('FB_PAGE_2_ID')]
    group_id = os.environ.get('FB_GROUP_1_ID') 

    if not access_token:
        logger.error("FB Access Token missing")
        return False

    try:
        # URL स्ट्रक्चर
        city_slug = instance.url_city if instance.url_city else "news"
        news_link = f"https://uttarworld.com/{city_slug}/{instance.slug}/"
        
        msg = f"{instance.title}\n\nपूरी खबर यहाँ पढ़ें: {news_link}\n\n#UttarWorld #UPNews #{instance.district}"
        
        api_version = "v21.0"
        
        if instance.image_url:
            payload = {'url': instance.image_url, 'caption': msg, 'access_token': access_token}
            suffix = "/photos"
        else:
            payload = {'message': msg, 'link': news_link, 'access_token': access_token}
            suffix = "/feed"

        # Pages और Groups पर पोस्ट
        for p_id in page_ids:
            if p_id:
                requests.post(f"https://graph.facebook.com/{api_version}/{p_id}{suffix}", data=payload, timeout=20)

        if group_id:
            requests.post(f"https://graph.facebook.com/{api_version}/{group_id}{suffix}", data=payload, timeout=20)

        return True
    except Exception as e:
        logger.error(f"FB Auto-Post Error: {e}")
        return False