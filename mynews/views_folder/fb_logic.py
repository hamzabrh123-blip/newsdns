import requests
from io import BytesIO
from PIL import Image
from django.http import HttpResponse
from .config import FB_ACCESS_TOKEN, FB_PAGE_ID, SITE_URL

def post_to_facebook_network(title, slug, url_city, image_url=None):
    """Facebook Page par auto-post karne ke liye"""
    if not FB_ACCESS_TOKEN or not FB_PAGE_ID:
        print("FB Error: Credentials missing!")
        return 
        
    news_url = f"{SITE_URL}/{url_city}/{slug}.html"
    fb_url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed"
    
    # Image logic: Agar ImgBB link hai toh wahi use karo, warna static logo
    if image_url and image_url.startswith('http'):
        final_img = image_url
    elif image_url:
        final_img = f"{SITE_URL}{image_url}"
    else:
        final_img = f"{SITE_URL}/static/logo.png"

    payload = {
        'message': title,
        'link': news_url,
        'picture': final_img,
        'access_token': FB_ACCESS_TOKEN
    }

    try:
        response = requests.post(fb_url, data=payload, timeout=30)
        res_data = response.json()
        if response.status_code == 200:
            print(f"FB Success! ID: {res_data.get('id')}")
        else:
            print(f"FB Error: {res_data.get('error', {}).get('message')}")
    except Exception as e:
        print(f"FB Request Failed: {e}")

# --- IMAGE CONVERSION LOGIC (Isi file mein) ---

def get_converted_image_response(img_url):
    """WebP ko JPG mein badal kar HttpResponse return karta hai"""
    if not img_url:
        return HttpResponse(status=400)
    try:
        resp = requests.get(img_url, timeout=10)
        img = Image.open(BytesIO(resp.content))
        
        # JPG Conversion
        img = img.convert('RGB')
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        
        return HttpResponse(buffer.getvalue(), content_type="image/jpeg")
    except Exception as e:
        print(f"Conversion Error: {e}")
        return HttpResponse(status=404)
