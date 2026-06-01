import os
import requests
import base64
import io
import logging
import json # ⚡ YE IMPORT MISSING THA!
import gc
from PIL import Image
from django.conf import settings
from django.contrib.staticfiles import finders

logger = logging.getLogger(__name__)

# --- 1. IMAGE ENGINE (Optimized) ---
def process_and_upload_to_imgbb(instance, is_shop=True):
    image_field = getattr(instance, 'image', None)
    if not image_field or not hasattr(image_field, 'file'): return None

    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key: return None

    try:
        # Use content from the file object
        image_content = image_field.read()
        if not image_content: return None
        
        with Image.open(io.BytesIO(image_content)) as img:
            img = img.convert('RGBA')
            
            # Shopping logo processing
            logo_path = finders.find('images/uttarworld-shopping-icon.png')
            if logo_path and os.path.exists(logo_path):
                with Image.open(logo_path).convert("RGBA") as logo:
                    ratio = 0.15
                    logo_w = int(img.width * ratio)
                    logo_h = int(logo.height * (logo_w / logo.width))
                    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                    img.paste(logo, (img.width - logo_w - 20, 20), logo)

            img = img.convert("RGB")
            if img.width > 1200: 
                img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            img.save(output, format='WEBP', quality=75, optimize=True)
            base64_image = base64.b64encode(output.getvalue())

        # Request to ImgBB
        response = requests.post(
            "https://api.imgbb.com/1/upload", 
            data={"key": api_key, "image": base64_image}, 
            timeout=20
        )
        
        if response.status_code == 200:
            return response.json()['data']['url']
        return None
        
    except Exception as e:
        logger.error(f"Image Upload Error: {e}")
        return None

# --- 2. GOOGLE INDEXING API (Fixed) ---
def ping_google_indexing(url):
    try:
        json_file_path = os.path.join(settings.BASE_DIR, 'credentials.json')
        with open(json_file_path, 'r') as f:
            creds_data = json.load(f) # Ab ye kaam karega

        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
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
        return f"✅ Indexing Success: {response.status_code}"
            
    except Exception as e:
        return f"❌ Indexing Error: {str(e)}"