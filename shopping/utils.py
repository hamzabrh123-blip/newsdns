import os
import requests
import base64
import io
from PIL import Image
from django.conf import settings
from django.contrib.staticfiles import finders

def process_and_upload_to_imgbb(instance):
    # अब यह सीधे Render के Environment से चाबी उठाएगा
    api_key = os.environ.get("IMGBB_API_KEY") 
    
    # अगर वहां नहीं मिली, तो settings.py में ढूंढेगा
    if not api_key:
        api_key = getattr(settings, "IMGBB_API_KEY", None)

    if not api_key:
        print("DEBUG ERROR: Bhai Key kahin nahi mil rahi!")
        return None

    try:
        if not instance.image:
            return None
            
        # अगर पहले से अपलोड है तो दोबारा मेहनत न करे
        current_url = str(instance.image_url) if instance.image_url else ""
        if "i.ibb.co" in current_url:
            return None
            
        image_file = instance.image
        image_file.seek(0)
        img = Image.open(image_file)
        
        # RGBA to RGB (White background fix)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            background.paste(img, (0, 0), img)
            img = background
        else:
            img = img.convert('RGB')

        # Resize to 800px
        if img.width > 800:
            new_height = int(img.height * (800 / img.width))
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)

        # Watermark Logic
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
        except Exception as logo_err:
            print(f"Logo skipped: {logo_err}")

        # WebP Compression (Target 25KB)
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

        # ImgBB Upload
        output.seek(0)
        encoded_string = base64.b64encode(output.read())
        
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": encoded_string},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['data']['url']
        
    except Exception as e:
        print(f"Upload logic fail: {e}")
    
    return None
