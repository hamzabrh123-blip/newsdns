import requests
import re
import base64
import os
from mynews.models import News
from mynews.config import FB_ACCESS_TOKEN, FB_PAGE_ID, SITE_URL

# --- SIDEBAR LOGIC ---
def get_common_sidebar_data():
    return {
        "bazaar_sidebar": News.objects.filter(category="Market").order_by("-date")[:5],
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:10],
        "technology_sidebar": News.objects.filter(category="Technology").order_by("-date")[:3],
        "bollywood_sidebar": News.objects.filter(category="Bollywood").order_by("-date")[:3],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
    }

# --- IMGBB LOGIC ---
def upload_to_imgbb(image_field):
    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key: return None
    url = "https://api.imgbb.com/1/upload"
    try:
        image_field.open()
        image_data = base64.b64encode(image_field.read())
        image_field.close()
        payload = {"key": api_key, "image": image_data}
        response = requests.post(url, data=payload, timeout=30)
        return response.json()['data']['url'] if response.status_code == 200 else None
    except: return None

# --- FACEBOOK LOGIC ---
def post_to_facebook_network(title, slug, url_city):
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID: return 
    news_url = f"{SITE_URL}/{url_city}/{slug}.html"
    fb_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    payload = {'message': f"🔥 {title}\n\nपूरी खबर यहाँ पढ़ें 👇", 'link': news_url, 'access_token': FB_ACCESS_TOKEN}
    try: requests.post(fb_url, data=payload, timeout=60)
    except: pass

# --- VIDEO LOGIC ---
def extract_video_id(url):
    if not url: return None
    match = re.search(r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})", url)
    return match.group(1) if match else None