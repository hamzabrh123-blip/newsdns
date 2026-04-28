import requests
import base64
import io
import os
from PIL import Image
try:
    import pillow_avif # AVIF सपोर्ट के लिए
except ImportError:
    pass
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
        
        # ओरिजिनल फॉर्मेट को RGB में बदलें (सफेद बैकग्राउंड के साथ ताकि काला न दिखे)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            background.paste(img, (0, 0), img)
            img = background
        else:
            img = img.convert('RGB')

        # 2. लोगो वाटरमार्क
        logo_path = finders.find('images/uttarworld-shopping-icon.png')
        if logo_path:
            with Image.open(logo_path) as logo:
                logo = logo.convert('RGBA')
                
                # लोगो साइज (चौड़ाई का 15%)
                logo_w = int(img.width * 0.15)
                logo_h = int(logo.height * (logo_w / logo.width))
                logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                
                # पोजीशन (Bottom-Right, 20px गैप)
                pos = (img.width - logo_w - 20, img.height - logo_h - 20)
                
                # इमेज पर लोगो लगाएं
                img.paste(logo, pos, logo)
        else:
            print("Logo Warning: Path not found, uploading without watermark.")

        # 3. WebP Conversion (Best for Performance)
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=85, optimize=True) # Quality 85 is sweet spot
        output.seek(0)

        # 4. Upload to ImgBB
        encoded_string = base64.b64encode(output.read())
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": encoded_string},
            timeout=30
        )
        
        if response.status_code == 200:
            res_data = response.json()
            if 'data' in res_data and 'url' in res_data['data']:
                return res_data['data']['url']
        
        print(f"ImgBB Error: {response.text}")
        
    except Exception as e:
        print(f"Final Upload Error: {e}")
    
    return None
