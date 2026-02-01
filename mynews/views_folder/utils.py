import requests
import re
from .models import News
from .config import FB_ACCESS_TOKEN, FB_PAGE_ID, SITE_URL

def get_common_sidebar_data():
    return {
        "bazaar_sidebar": News.objects.filter(category="Market").order_by("-date")[:5],
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:10],
        "technology_sidebar": News.objects.filter(category="Technology").order_by("-date")[:3],
        "bollywood_sidebar": News.objects.filter(category="Bollywood").order_by("-date")[:3],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
    }

def post_to_facebook_network(title, slug, url_city):
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID: return 
    news_url = f"{SITE_URL}/{url_city}/{slug}.html"
    fb_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    payload = {'message': f"🔥 {title}\n\nपूरी खबर यहाँ पढ़ें 👇", 'link': news_url, 'access_token': FB_ACCESS_TOKEN}
    try: requests.post(fb_url, data=payload, timeout=60)
    except: pass

def extract_video_id(url):
    if not url: return None
    match = re.search(r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})", url)
    return match.group(1) if match else None