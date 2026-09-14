import os
import requests
import base64
import io
import logging
import json
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
        image_content = image_field.read()
        if not image_content: return None
        
        with Image.open(io.BytesIO(image_content)) as img:
            img = img.convert('RGBA')
            
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

# --- 2. AUTOMATIC STORE & LOGO DETECTION ENGINE (Strict Sequence) ---
def detect_store_and_logo(title, url):
    """
    Step 1: Pehle URL check karo. Agar non-Amazon platform hai toh seedha wahi return karo.
    Step 2: Agar Amazon/Generic link hai, tab title se brand match karke Amazon ke andar ka logo uthao.
    """
    url_lower = url.lower() if url else ""
    title_clean = title.lower().replace(".", "").replace(" ", "") if title else ""
    
    # STEP 1: Strict URL check for non-Amazon platforms (Return immediately)
    if 'ajiio.in' in url_lower or 'ajio.com' in url_lower:
        return {
            'store_name': 'AJIO',
            'logo_url': '/static/store_logo/ajio.png'
        }
    elif 'fktr.in' in url_lower or 'flipkart.com' in url_lower:
        return {
            'store_name': 'Flipkart',
            'logo_url': '/static/store_logo/flipkart.png'
        }
    elif 'myntr.it' in url_lower or 'myntra.com' in url_lower:
        return {
            'store_name': 'Myntra',
            'logo_url': '/static/store_logo/myntra.png'
        }
    elif 'meesho.com' in url_lower:
        return {
            'store_name': 'Meesho',
            'logo_url': '/static/store_logo/meesho.png'
        }
        
    # STEP 2: Default to Amazon, then check Title against brand logos folder
    detected_store = "Amazon"
    logo_filename = "amazon.png"
    
    logo_dir = os.path.join(settings.BASE_DIR, 'shopping', 'static', 'store_logo')
    if os.path.exists(logo_dir) and title_clean:
        for filename in os.listdir(logo_dir):
            if filename.endswith('.png'):
                brand_slug = filename.replace('.png', '').lower()
                # Main store names ko chhod kar specific brands match karo title mein
                if brand_slug not in ['amazon', 'flipkart', 'myntra', 'meesho', 'ajio']:
                    if brand_slug and brand_slug in title_clean:
                        detected_store = brand_slug.upper()
                        logo_filename = filename
                        break
                        
    return {
        'store_name': detected_store,
        'logo_url': f"/static/store_logo/{logo_filename}"
    }

# --- 3. GOOGLE INDEXING API (Fixed) ---
def ping_google_indexing(url):
    try:
        json_file_path = os.path.join(settings.BASE_DIR, 'credentials.json')
        with open(json_file_path, 'r') as f:
            creds_data = json.load(f)

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
    
# --- 4. PINTEREST PUBLISHING ENGINE ---
def publish_to_pinterest(title, description, image_url, destination_link, access_token):
    url = "https://api.pinterest.com/v5/pins"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": title[:100], 
        "description": description[:500], 
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        },
        "link": destination_link
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 201:
            logger.info(f"✅ Pinterest Success: {title}")
            return True, "Published"
        else:
            logger.error(f"❌ Pinterest Error ({response.status_code}): {response.text}")
            return False, response.text
            
    except Exception as e:
        logger.error(f"❌ Pinterest Connection Error: {e}")
        return False, str(e)