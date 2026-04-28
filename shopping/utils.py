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
    """
    1. इमेज को WebP में बदलता है।
    2. 'uttarworld-shopping-icon.png' लोगो चिपकाता है।
    3. ImgBB पर अपलोड करके URL देता है।
    """
    api_key = getattr(settings, 'IMGBB_API_KEY', None)
    if not api_key:
        print("Upload Error: IMGBB_API_KEY missing!")
        return None

    try:
        # 1. इमेज ओपन करें
        image_file.seek(0)
        img = Image.open(image_file)
        
        # ओरिजिनल को RGBA में बदलें ताकि लोगो सही से चिपके
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 2. लोगो चिपकाने का पक्का इंतज़ाम
        # finders.find सीधा 'images/uttarworld-shopping-icon.png' ढूंढेगा
        logo_path = finders.find('images/uttarworld-shopping-icon.png')
        
        if logo_path:
            logo = Image.open(logo_path).convert('RGBA')
            
            # लोगो साइज (चौड़ाई का 15%)
            logo_w = int(img.width * 0.15)
            logo_h = int(logo.height * (logo_w / logo.width))
            logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            
            # पोजीशन (Bottom-Right)
            pos = (img.width - logo_w - 20, img.height - logo_h - 20)
            
            # पेस्ट (Masking के साथ ताकि काला डब्बा न आए)
            img.paste(logo, pos, logo)
        else:
            print("Logo Error: Static path par logo nahi mila!")

        # 3. WebP Conversion
        img = img.convert('RGB') # Final conversion for WebP
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=80)
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
