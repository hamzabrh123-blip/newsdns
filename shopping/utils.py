import os
import requests
import base64
import io
import logging
import gc
from PIL import Image
from django.conf import settings
from django.contrib.staticfiles import finders
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# AVIF सपोर्ट
try:
    import pillow_avif
except ImportError:
    pass

logger = logging.getLogger(__name__)

# --- 1. IMAGE ENGINE (Shopping Focused) ---
def process_and_upload_to_imgbb(instance):
    """
    Shopping ke liye optimize ki gayi image function. 
    Sirf 'image' ya 'main_image' field se kaam karegi.
    """
    image_field = getattr(instance, 'image', None) or getattr(instance, 'main_image', None)
    if not image_field: return None

    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key: return None

    try:
        image_field.seek(0)
        img = Image.open(io.BytesIO(image_field.read())).convert('RGBA')
        
        # Shopping logo path
        logo_path = finders.find('images/uttarworld-shopping-icon.png')
        
        if logo_path and os.path.exists(logo_path):
            with Image.open(logo_path).convert("RGBA") as logo:
                ratio = 0.15 # Shopping logo ratio
                logo_w = int(img.width * ratio)
                logo_h = int(logo.height * (logo_w / logo.width))
                logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                pos = (img.width - logo_w - 20, 20) # Top-right position
                img.paste(logo, pos, logo)

        img = img.convert("RGB")
        if img.width > 1200: img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format='WEBP', quality=75, optimize=True)
        base64_image = base64.b64encode(output.getvalue())

        response = requests.post("https://api.imgbb.com/1/upload", data={"key": api_key, "image": base64_image}, timeout=30)
        img.close()
        gc.collect()
        return response.json()['data']['url'] if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Image Error: {e}")
        return None

# --- 2. GOOGLE INDEXING API (Fixed) ---
def ping_google_indexing(url):
    try:
        json_file_path = os.path.join(settings.BASE_DIR, 'credentials.json')
        with open(json_file_path, 'r') as f:
            creds_data = json.load(f)

        creds = service_account.Credentials.from_service_account_info(
            creds_data,
            scopes=['https://www.googleapis.com/auth/indexing']
        )
        
        auth_req = Request()
        creds.refresh(auth_req)
        
        payload = {'url': url, 'type': 'URL_UPDATED'}
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {creds.token}'}
        
        response = requests.post(
            'https://indexing.googleapis.com/v3/urlNotifications:publish', 
            json=payload, 
            headers=headers,
            timeout=20
        )
        return f"✅ Status: {response.status_code} | Details: {response.text}"
            
    except Exception as e:
        return f"❌ Indexing Exception: {str(e)}"