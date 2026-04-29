import requests
import base64
import io
from PIL import Image
from django.conf import settings
from django.contrib.staticfiles import finders

def upload_to_imgbb(image_file):
    api_key = getattr(settings, 'IMGBB_API_KEY', None)
    if not api_key:
        print("Upload Error: IMGBB_API_KEY missing!")
        return None

    try:
        # 1. इमेज ओपन करें
        image_file.seek(0)
        img = Image.open(image_file)
        
        # RGB Conversion (Safe for Transparency)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            background.paste(img, (0, 0), img)
            img = background
        else:
            img = img.convert('RGB')

        # [PROSESS 1: Resize] 
        # 25KB के लिए 800px चौड़ाई सबसे सही है
        if img.width > 800:
            new_height = int(img.height * (800 / img.width))
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)

        # [PROSESS 2: Logo Watermark]
        logo_path = finders.find('images/uttarworld-shopping-icon.png')
        if logo_path:
            with Image.open(logo_path) as logo:
                logo = logo.convert('RGBA')
                logo_w = int(img.width * 0.15)
                logo_h = int(logo.height * (logo_w / logo.width))
                logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                pos = (img.width - logo_w - 15, img.height - logo_h - 15)
                img.paste(logo, pos, logo)

        # [PROSESS 3: Strict 25KB Loop]
        quality = 80
        output = io.BytesIO()
        
        while True:
            output.seek(0)
            output.truncate()
            # WebP Conversion
            img.save(output, format="WEBP", quality=quality, optimize=True)
            file_size = output.tell() / 1024  # Size in KB
            
            # अगर 25KB से कम है, तो बाहर निकलो
            if file_size <= 25 or quality <= 15:
                break
            
            # क्वालिटी को 5-5 करके नीचे लाओ
            quality -= 5

        # 4. Final Upload
        output.seek(0)
        encoded_string = base64.b64encode(output.read())
        
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": encoded_string},
            timeout=30
        )
        
        if response.status_code == 200:
            res_data = response.json()
            return res_data['data']['url']
        
        print(f"ImgBB Error: {response.text}")
        
    except Exception as e:
        print(f"Final Upload Error: {e}")
    
    return None
