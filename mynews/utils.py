import requests
import re
import base64
import os
import logging
from django.conf import settings
from django.utils.text import slugify

logger = logging.getLogger(__name__)

# --- SIDEBAR LOGIC ---
def get_common_sidebar_data():
    # Circular import se bachne ke liye import andar rakha hai
    from mynews.models import News
    return {
        "bazaar_sidebar": News.objects.filter(category="Market").order_by("-date")[:5],
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:10],
        "technology_sidebar": News.objects.filter(category="Technology").order_by("-date")[:3],
        "bollywood_sidebar": News.objects.filter(category="Bollywood").order_by("-date")[:3],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow').order_by("-date")[:10],
    }

# --- IMGBB LOGIC (30-50KB Compressed Image Yahan Aayegi) ---
def upload_to_imgbb(image_field):
    # Seedha Render ke Environment Variable se key uthayega
    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        logger.error("ImgBB API Key missing in environment variables!")
        return None

    url = "https://api.imgbb.com/1/upload"
    try:
        # Image field ko read karke base64 banana
        image_field.open()
        image_data = base64.b64encode(image_field.read())
        image_field.close()

        payload = {
            "key": api_key,
            "image": image_data,
        }
        # Timeout 60 seconds rakha hai taaki slow internet par fail na ho
        response = requests.post(url, data=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()['data']['url']
        else:
            logger.error(f"ImgBB API Error: {response.json()}")
            return None
    except Exception as e:
        logger.error(f"ImgBB Upload Exception: {e}")
        return None

# --- FACEBOOK NETWORK LOGIC ---
def post_to_facebook_network(title, slug, url_city, image_url=None):
    # Settings se tokens uthana best hai
    access_token = os.environ.get("FB_ACCESS_TOKEN")
    page_id = os.environ.get("FB_PAGE_ID")
    site_url = "https://uttarworld.com"

    if not access_token or not page_id:
        print("FB Credentials missing in Render Environment!")
        return 

    # Django ke reverse URL pattern ke hisaab se URL banaya
    news_url = f"{site_url}/{url_city}/{slug}/"
    fb_url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    
    payload = {
        'message': f"🔴 {title}\n\nपूरी खबर यहाँ पढ़ें: {news_url}", 
        'link': news_url, 
        'access_token': access_token
    }

    # Agar ImgBB ka link hai toh wahi use karo, varna logo
    if image_url:
        payload['picture'] = image_url
    else:
        payload['picture'] = f"{site_url}/static/logo.png"

    try:
        response = requests.post(fb_url, data=payload, timeout=60)
        if response.status_code != 200:
            print(f"FB Post Error: {response.json()}")
    except Exception as e:
        print(f"FB Connection Error: {e}")

# --- VIDEO ID EXTRACTION ---
def extract_video_id(url):
    if not url:
        return None
    # Youtube ke saare formats (Shorts, Embed, Mobile) ke liye regex
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None
