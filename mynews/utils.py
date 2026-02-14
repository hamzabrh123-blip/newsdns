import requests
import re
import base64
import os
import logging
import gc
import io
from PIL import Image
from django.conf import settings
from django.apps import apps # <--- Ye zaroori hai loop todne ke liye

logger = logging.getLogger(__name__)

# --- SIDEBAR LOGIC (FIXED) ---
def get_common_sidebar_data():
    try:
        # Circular import se bachne ke liye apps.get_model use karo
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

# --- IMAGE PROCESSING & IMGBB (MEMORY SAFE) ---
def process_and_upload_to_imgbb(instance):
    if not instance.image or instance.image_url:
        return None

    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        return None

    try:
        img = Image.open(instance.image)
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        img.thumbnail((1200, 1200))

        # Watermark
        try:
            w_path = os.path.join(settings.BASE_DIR, 'mynews', 'static', 'watermark.png')
            if os.path.exists(w_path):
                with Image.open(w_path).convert("RGBA") as w_img:
                    w_img.thumbnail((img.width // 4, img.height // 4))
                    img.paste(w_img, (img.width - w_img.width - 20, img.height - w_img.height - 20), w_img)
        except: pass

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        image_data = base64.b64encode(output.getvalue())

        payload = {"key": api_key, "image": image_data}
        response = requests.post("https://api.imgbb.com/1/upload", data=payload, timeout=25)
        
        # Memory cleanup
        img.close()
        output.close()
        gc.collect()

        if response.status_code == 200:
            return response.json()['data']['url']
        return None
    except Exception as e:
        logger.error(f"ImgBB Error: {e}")
        return None

# --- FACEBOOK AUTO-POST (FIXED URL) ---
def post_to_facebook(instance):
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_id = os.environ.get('FB_PAGE_ID')

    if not access_token or not page_id:
        return False

    try:
        news_link = f"https://uttarworld.com/news/{instance.slug}/"
        # 1. कैप्शन को छोटा और साफ़ रखें
        msg = f"{instance.title}\n\nपूरी खबर पढ़ें यहाँ: {news_link}"
        
        # 2. अगर image_url है, तो सीधा 'photos' endpoint पर पोस्ट करें
        if instance.image_url:
            fb_url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
            payload = {
                'url': instance.image_url, # सीधा ImgBB वाला लिंक
                'caption': msg,            # कैप्शन में टेक्स्ट और लिंक
                'access_token': access_token
            }
        else:
            # बैकअप: अगर फोटो नहीं है तो पुराना तरीका (बिना फोटो वाली पोस्ट)
            fb_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            payload = {
                'message': msg,
                'link': news_link,
                'access_token': access_token
            }
        
        response = requests.post(fb_url, data=payload, timeout=20)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"FB Error: {e}")
        return False

def extract_video_id(url):
    if not url: return None
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None
