import requests
import base64
import io
from PIL import Image
from django.conf import settings
from django.contrib.staticfiles import finders

def upload_to_imgbb(image_file):
    """
    1. इमेज को WebP में बदलता है।
    2. 'uttarworld-shopping-icon.png' लोगो को नीचे दाएं कोने में लगाता है।
    3. ImgBB पर अपलोड करके URL देता है।
    """
    api_key = getattr(settings, 'IMGBB_API_KEY', None)
    if not api_key:
        print("Upload Error: IMGBB_API_KEY is not defined in settings.py")
        return None

    try:
        # 1. इमेज को Pillow से ओपन करें
        image_file.seek(0)
        img = Image.open(image_file)
        
        # अगर इमेज RGBA है तो उसे RGB में बदलें (WebP के लिए बेहतर है)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 2. लोगो चिपकाने का तड़का (Corner Logo)
        logo_path = finders.find('images/uttarworld-shopping-icon.png')
        if logo_path:
            logo = Image.open(logo_path)
            
            # लोगो का साइज मेन इमेज की चौड़ाई का 15% रखें
            logo_width = int(img.width * 0.15)
            logo_height = int(logo.height * (logo_width / logo.width))
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            
            # पोजीशन: नीचे से 20px और दाएं से 20px छोड़ कर
            padding = 20
            position = (img.width - logo_width - padding, img.height - logo_height - padding)
            
            # लोगो पेस्ट करें (Transparency के साथ)
            if logo.mode == 'RGBA':
                img.paste(logo, position, logo)
            else:
                img.paste(logo, position)

        # 3. इमेज को मेमोरी (BytesIO) में WebP फॉर्मेट में सेव करें
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=80)
        output.seek(0)

        # 4. Base64 Encoding
        encoded_string = base64.b64encode(output.read())
        
        # 5. ImgBB API Request
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": api_key,
            "image": encoded_string,
        }
        
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            return response.json()['data']['url']
        else:
            print(f"ImgBB API Error: {response.text}")
            
    except Exception as e:
        print(f"Branding & Upload Error: {e}")
    
    return None
