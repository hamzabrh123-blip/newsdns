import requests
import re
import base64
import os
import logging
import gc
import io
from PIL import Image
from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)

# --- 1. SIDEBAR LOGIC (AdSense के लिए Fast Loading) ---
def get_common_sidebar_data():
    try:
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

# --- 2. IMAGE PROCESSING (AVIF/WebP + Watermark + Low RAM Fix) ---
def process_and_upload_to_imgbb(instance):
    image_field = getattr(instance, 'image', None)
    # अगर image_url पहले से है तो दोबारा अपलोड न करें
    if not image_field or (hasattr(instance, 'image_url') and instance.image_url):
        return None

    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        logger.warning("IMGBB_API_KEY missing")
        return None

    try:
        # RAM बचाने के लिए
        img_data = image_field.read()
        img = Image.open(io.BytesIO(img_data))

        # 1. AVIF/WebP को RGB में बदलें (ताकि वॉटरमार्क एरर न दे)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        
        # 2. Resizing: 512MB RAM के लिए (800px चौड़ाई SEO के लिए बेस्ट है)
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)

        # 3. Watermark Logic
        try:
            w_path = os.path.join(settings.BASE_DIR, 'mynews', 'static', 'watermark.png')
            if os.path.exists(w_path):
                with Image.open(w_path).convert("RGBA") as w_img:
                    # वॉटरमार्क छोटा रखें (15% चौड़ाई)
                    w_width = int(img.width * 0.15)
                    w_height = int(w_img.height * (w_width / w_img.width))
                    w_img = w_img.resize((w_width, w_height), Image.Resampling.LANCZOS)
                    
                    # Bottom Right Position
                    pos = (img.width - w_img.width - 10, img.height - w_img.height - 10)
                    img.paste(w_img, pos, w_img)
        except Exception as we:
            logger.error(f"Watermark Error: {we}")

        # 4. Save as JPEG (High Compression for Speed)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=70, optimize=True) # Quality 70 is ideal
        base64_image = base64.b64encode(output.getvalue())

        # Clean Up Memory
        img.close()
        del img_data
        gc.collect()

        # 5. ImgBB Upload
        payload = {"key": api_key, "image": base64_image}
        response = requests.post("https://api.imgbb.com/1/upload", data=payload, timeout=30)

        if response.status_code == 200:
            return response.json()['data']['url']
        
        return None

    except Exception as e:
        logger.error(f"ImgBB Processing Error: {e}")
        return None
    finally:
        gc.collect()

# --- 3. FACEBOOK AUTO-POST (Fixed Image & Link Logic) ---
def post_to_facebook(instance):
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_ids = [os.environ.get('FB_PAGE_ID'), os.environ.get('FB_PAGE_2_ID')]
    group_id = os.environ.get('FB_GROUP_1_ID') 

    if not access_token:
        return False

    try:
        city_slug = instance.url_city if instance.url_city else "news"
        news_link = f"https://uttarworld.com/{city_slug}/{instance.slug}/"
        
        # फेसबुक पर दिखाने के लिए साफ़ मैसेज
        msg = f"{instance.title}\n\nपूरी खबर यहाँ पढ़ें: {news_link}"
        
        api_version = "v21.0"
        
        # --- सबसे ज़रूरी सुधार: 'url' पैरामीटर के साथ 'message' भेजना ---
        # अगर image_url (ImgBB वाली) है, तो उसे 'url' में भेजें
        if instance.image_url:
            payload = {
                'url': instance.image_url, 
                'message': msg, # Photos endpoint में 'message' काम करता है, 'caption' पुराना हो गया
                'access_token': access_token
            }
            suffix = "/photos"
        else:
            payload = {
                'message': msg, 
                'link': news_link, 
                'access_token': access_token
            }
            suffix = "/feed"

        # Pages पर पोस्ट
        for p_id in page_ids:
            if p_id:
                requests.post(f"https://graph.facebook.com/{api_version}/{p_id}{suffix}", data=payload, timeout=20)

        # Groups पर पोस्ट
        if group_id:
            requests.post(f"https://graph.facebook.com/{api_version}/{group_id}{suffix}", data=payload, timeout=20)

        return True
    except Exception as e:
        logger.error(f"FB Post Error: {e}")
        return False
