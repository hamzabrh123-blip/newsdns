import requests
from .config import FB_ACCESS_TOKEN, FB_PAGE_ID, SITE_URL

def post_to_facebook_network(title, slug, url_city, image_url=None):
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID:
        print("FB Error: Credentials missing!")
        return 
        
    news_url = f"{SITE_URL}/{url_city}/{slug}.html"
    fb_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    
    # Ekdum Clean Payload: No extra text, no emojis
    payload = {
        'message': title,  # Sirf headline jayegi upar
        'link': news_url,  # Link se FB khud card bana lega
        'access_token': FB_ACCESS_TOKEN
    }

    # Image URL fix: Full path bhej rahe hain taaki FB preview sahi dikhaye
    if image_url:
        payload['picture'] = f"{SITE_URL}{image_url}"
    else:
        payload['picture'] = f"{SITE_URL}/static/logo.png"

    try:
        response = requests.post(fb_url, data=payload, timeout=60)
        result = response.json()
        
        if response.status_code != 200:
            print(f"FB Post Failed: {result.get('error', {}).get('message')}")
        else:
            print(f"FB Post Success! ID: {result.get('id')}")
            
    except Exception as e:
        print(f"Network Error: {str(e)}")
