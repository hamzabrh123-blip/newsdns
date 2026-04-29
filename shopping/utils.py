import os
import requests
import base64
import io
import logging
from PIL import Image
from django.conf import settings
from django.contrib.staticfiles import finders

# Logs देखने के लिए logger सेट किया
logger = logging.getLogger(__name__)

def process_and_upload_to_imgbb(instance):
    # 1. API Key चेक करना
    api_key = os.environ.get("IMGBB_API_KEY") 
    if not api_key:
        api_key = getattr(settings, "IMGBB_API_KEY", None)

    if not api_key:
        logger.error("CRITICAL ERROR: ImgBB API Key is missing in Render/Settings!")
        return None

    try:
        if not instance.image:
            return None
            
        # 2. अगर पहले से i.ibb.co का लिंक है, तो दोबारा अपलोड न करे
        current_url = str(instance.image_url) if instance.image_url else ""
        if "i.ibb.co" in current_url:
            return None
            
        image_file = instance.image
        image_file.seek(0)
        img = Image.open(image_file)
        
        # 3. RGBA to RGB (Transparent background fix)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            background.paste(img, (0, 0), img)
            img = background
        else:
            img = img.convert('RGB')

        # 4. Resize (Max 800px width)
        if img.width > 800:
            new_height = int(img.height * (800 / img.width))
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)

        # 5. Watermark Logic
        try:
            logo_path = finders.find('images/uttarworld-shopping-icon.png')
            if logo_path and os.path.exists(logo_path):
                with Image.open(logo_path) as logo:
                    logo = logo.convert('RGBA')
                    logo_w = int(img.width * 0.15)
                    logo_h = int(logo.height * (logo_w / logo.width))
                    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                    pos = (img.width - logo_w - 15, img.height - logo_h - 15)
                    img.paste(logo, pos, logo)
            else:
                logger.warning(f"Watermark not found at: {logo_path}")
        except Exception as logo_err:
            logger.error(f"Watermark processing failed: {logo_err}")

        # 6. WebP Compression (Target 25KB)
        quality = 80
        output = io.BytesIO()
        while True:
            output.seek(0)
            output.truncate()
            img.save(output, format="WEBP", quality=quality, optimize=True)
            file_size = output.tell() / 1024
            if file_size <= 25 or quality <= 10:
                break
            quality -= 10

        # 7. ImgBB Upload
        output.seek(0)
        encoded_string = base64.b64encode(output.read())
        
        logger.info(f"Uploading to ImgBB... Size: {file_size:.2f} KB")
        
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": encoded_string},
            timeout=30
        )
        
        if response.status_code == 200:
            final_url = response.json()['data']['url']
            logger.info(f"Upload Success! URL: {final_url}")
            return final_url
        else:
            logger.error(f"ImgBB Failed! Status: {response.status_code}, Response: {response.text}")
        
    except Exception as e:
        logger.error(f"Logic failure in process_and_upload_to_imgbb: {str(e)}")
    
    return None
