import requests
import re
import base64
import os
import logging
import gc
import io
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

# --- SIDEBAR LOGIC ---
def get_common_sidebar_data():
    try:
        from mynews.models import News
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

# --- IMAGE PROCESSING (WATERMARK) & IMGBB LOGIC ---
def process_and_upload_to_imgbb(instance):
    """Image को watermark करना और ImgBB पर अपलोड करना (Memory Efficient)"""
    if not instance.image or instance.image_url:
        return None

    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        logger.error("ImgBB API Key missing!")
        return None

    try:
        # 1. Image Processing
        img = Image.open(instance.image)
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Resize if too big
        img.thumbnail((1200, 1200))

        # Watermark add karna
        try:
            w_path = os.path.join(settings.BASE_DIR, 'mynews', 'static', 'watermark.png')
            if os.path.exists(w_path):
                with Image.open(w_path).convert("RGBA") as w_img:
                    # Watermark size set karein (Image ka 25%)
                    w_img.thumbnail((img.width // 4, img.height // 4))
                    # Bottom-right corner mein paste karein
                    img.paste(w_img, (img.width - w_img.width - 20, img.height - w_img.height - 20), w_img)
        except Exception as we:
            logger.warning(f"Watermark skip hua: {we}")

        # 2. Binary Conversion for Upload
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        raw_data = output.getvalue()
        image_data = base64.b64encode(raw_data)

        # 3. ImgBB Upload
        payload = {
            "key": api_key,
            "image": image_data,
        }
        response = requests.post("https://api.imgbb.com/1/upload", data=payload, timeout=25)
        
        # Cleanup Memory
        output.close()
        img.close()
        del raw_data
        del image_data
        gc.collect()

        if response.status_code == 200:
            return response.json()['data']['url']
        return None

    except Exception as e:
        logger.error(f"Image Processing/Upload Error: {e}")
        return None

# --- FACEBOOK AUTO-POST LOGIC ---
def post_to_facebook(instance):
    """Published news को Facebook Page पर शेयर करना"""
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_id = os.environ.get('FB_PAGE_ID')

    if not access_token or not page_id:
        logger.error("FB Credentials missing!")
        return False

    # Full news URL prepare karna
    site_url = "https://uttarworld.com"
    news_link = f"{site_url}{instance.get_absolute_url()}"
    
    msg = f"{instance.title}\n\nपूरी खबर पढ़ें: {news_link}"
    
    payload = {
        'message': msg,
        'link': news_link,
        'access_token': access_token
    }

    try:
        fb_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        response = requests.post(fb_url, data=payload, timeout=20)
        
        if response.status_code == 200:
            logger.info(f"FB Post Success: {instance.id}")
            return True
        else:
            logger.error(f"FB API Error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"FB Connection Error: {e}")
        return False

# --- VIDEO ID EXTRACTION (Supports Shorts & Normal) ---
def extract_video_id(url):
    if not url:
        return None
    # Updated regex for YouTube Shorts
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None
