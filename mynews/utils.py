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

# --- SIDEBAR LOGIC ---
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

# --- IMAGE PROCESSING & IMGBB ---
def process_and_upload_to_imgbb(instance):
    if not instance.image or instance.image_url:
        return None

    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        logger.warning("IMGBB_API_KEY not found in environment")
        return None

    try:
        img = Image.open(instance.image)
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        img.thumbnail((1200, 1200))

        # --- Watermark Logic ---
        try:
            w_path = os.path.join(settings.BASE_DIR, 'mynews', 'static', 'watermark.png')
            if os.path.exists(w_path):
                with Image.open(w_path).convert("RGBA") as w_img:
                    # Watermark size: 25% of the main image
                    w_img.thumbnail((img.width // 4, img.height // 4))
                    img.paste(w_img, (img.width - w_img.width - 20, img.height - w_img.height - 20), w_img)
        except Exception as we:
            logger.error(f"Watermark Error: {we}")

        # --- Memory Optimized Saving ---
        with io.BytesIO() as output:
            img.save(output, format='JPEG', quality=85, optimize=True)
            image_data = base64.b64encode(output.getvalue())

            payload = {"key": api_key, "image": image_data}
            response = requests.post("https://api.imgbb.com/1/upload", data=payload, timeout=25)
        
        img.close()
        gc.collect()

        if response.status_code == 200:
            return response.json()['data']['url']
        return None
    except Exception as e:
        logger.error(f"ImgBB Error: {e}")
        return None

# --- FACEBOOK PAGE & GROUP AUTO-POST (RE-OPTIMIZED) ---
def post_to_facebook(instance):
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_ids = [os.environ.get('FB_PAGE_ID'), os.environ.get('FB_PAGE_2_ID')]
    group_id = os.environ.get('FB_GROUP_1_ID') 

    if not access_token:
        logger.error("FB Access Token missing in Render environment")
        return False

    try:
        # URL Logic: match your news_detail URL pattern
        city_slug = instance.url_city if instance.url_city else "news"
        news_link = f"https://uttarworld.com/{city_slug}/{instance.slug}/"
        
        msg = f"{instance.title}\n\nपूरी खबर यहाँ पढ़ें: {news_link}\n\n#UttarWorld #UPNews #{instance.district}"
        
        # API Payload Setup
        if instance.image_url:
            payload = {'url': instance.image_url, 'caption': msg, 'access_token': access_token}
            suffix = "/photos"
        else:
            payload = {'message': msg, 'link': news_link, 'access_token': access_token}
            suffix = "/feed"

        api_version = "v21.0" # Latest API Version
        
        # 1. Post to Pages
        for p_id in page_ids:
            if p_id:
                res = requests.post(f"https://graph.facebook.com/{api_version}/{p_id}{suffix}", data=payload, timeout=20)
                logger.info(f"FB Page {p_id} Response: {res.status_code}")

        # 2. Post to Group
        if group_id:
            res_group = requests.post(f"https://graph.facebook.com/{api_version}/{group_id}{suffix}", data=payload, timeout=20)
            logger.info(f"FB Group Response: {res_group.status_code}")

        return True
    except Exception as e:
        logger.error(f"FB Auto-Post Error: {e}")
        return False

def extract_video_id(url):
    if not url: return None
    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/|youtube-nocookie\.com\/embed\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    return match.group(1) if match else None
