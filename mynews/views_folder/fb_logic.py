import requests
from .config import FB_ACCESS_TOKEN, FB_PAGE_ID, SITE_URL

def post_to_facebook_network(title, slug, url_city):
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID:
        return 
        
    news_url = f"{SITE_URL}/{url_city}/{slug}.html"
    fb_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    payload = {
        'message': f"🔥 {title}\n\nपूरी खबर यहाँ पढ़ें 👇",
        'link': news_url,
        'access_token': FB_ACCESS_TOKEN
    }
    try:
        requests.post(fb_url, data=payload, timeout=60)
    except:
        pass