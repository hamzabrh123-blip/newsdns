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
        
        img.close()
        output.close()
        gc.collect()

        if response.status_code == 200:
            return response.json()['data']['url']
        return None
    except Exception as e:
        logger.error(f"ImgBB Error: {e}")
        return None

# --- FACEBOOK PAGE & GROUP AUTO-POST (FIXED) ---
def post_to_facebook(instance):
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_id = os.environ.get('FB_PAGE_ID')
    page2_id = os.environ.get('FB_PAGE_2_ID')
    group_id = os.environ.get('FB_GROUP_1_ID') 

    if not access_token:
        logger.error("FB Access Token missing in Render environment")
        return False

    try:
        news_link = f"https://uttarworld.com/news/{instance.slug}/"
        msg = f"{instance.title}\n\nपूरी खबर यहाँ पढ़ें: {news_link}"
        
        # Payload setup
        if instance.image_url:
            payload = {'url': instance.image_url, 'caption': msg, 'access_token': access_token}
            suffix = "/photos"
        else:
            payload = {'message': msg, 'link': news_link, 'access_token': access_token}
            suffix = "/feed"

        # 1. Post to Page 1
        if page_id:
            res_page = requests.post(f"https://graph.facebook.com/v18.0/{page_id}{suffix}", data=payload, timeout=20)
            logger.info(f"Page 1 Response: {res_page.status_code}")
            
        # 2. Post to Page 2 (FIXED: अलग endpoint बनाया)
        if page2_id:
            res_page2 = requests.post(f"https://graph.facebook.com/v18.0/{page2_id}{suffix}", data=payload, timeout=20)
            logger.info(f"Page 2 Response: {res_page2.status_code}")

        # 3. Post to Group
        if group_id:
            res_group = requests.post(f"https://graph.facebook.com/v18.0/{group_id}{suffix}", data=payload, timeout=20)
            logger.info(f"Group Response: {res_group.status_code}")

        return True
    except Exception as e:
        logger.error(f"FB Full Auto-Post Error: {e}")
        return False

def extract_video_id(url):
    if not url: return None
    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/|youtube-nocookie\.com\/embed\/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None
