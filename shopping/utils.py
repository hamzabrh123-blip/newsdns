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
        
        # अगर इमेज में ट्रांसपेरेंसी है, तो उसे सफेद बैकग्राउंड पर पेस्ट करें 
        # ताकि RGB कन्वर्जन में काला डब्बा न बने
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            background.paste(img, (0, 0), img)
            img = background
        else:
            img = img.convert('RGB')

        # 2. लोगो चिपकाने का इंतज़ाम
        logo_path = finders.find('images/uttarworld-shopping-icon.png')
        
        if logo_path:
            logo = Image.open(logo_path).convert('RGBA')
            
            # लोगो साइज (चौड़ाई का 15%)
            logo_w = int(img.width * 0.15)
            logo_h = int(logo.height * (logo_w / logo.width))
            logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            
            # पोजीशन (Bottom-Right, 20px गैप)
            pos = (img.width - logo_w - 20, img.height - logo_h - 20)
            
            # लोगो पेस्ट करें (लोगो खुद मास्क की तरह काम करेगा)
            img.paste(logo, pos, logo)
            logo.close() # मेमोरी बचाओ
        else:
            print("Logo Warning: Logo path nahi mila, bina logo ke upload ho raha hai!")

        # 3. WebP Conversion (Best for SEO and Performance)
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=80, optimize=True)
        output.seek(0)

        # 4. Upload to ImgBB
        encoded_string = base64.b64encode(output.read())
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": encoded_string},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['data']['url']
        else:
            print(f"ImgBB Response Error: {response.text}")
        
    except Exception as e:
        print(f"Final Upload Error: {e}")
    
    return None
