import os
import requests
import base64
import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)

def process_and_upload_to_imgbb(instance):
    # तुम्हारी नई वाली चाबी यहाँ से लोड होगी
    api_key = os.environ.get("IMGBB_API_KEY") 

    if not api_key:
        logger.error("Bhai, Render me Key nahi mili!")
        return None

    try:
        if not instance.image:
            return None
            
        image_file = instance.image
        image_file.seek(0)
        img = Image.open(image_file)
        
        # RGB Conversion & Resize (800px)
        img = img.convert('RGB')
        if img.width > 800:
            img = img.resize((800, int(img.height * (800 / img.width))), Image.Resampling.LANCZOS)

        # WebP Compression
        output = io.BytesIO()
        img.save(output, format="WEBP", quality=70, optimize=True)
        output.seek(0)
        
        # ImgBB POST Request (v1)
        encoded_string = base64.b64encode(output.read())
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": encoded_string},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['data']['url']
        
    except Exception as e:
        logger.error(f"Upload fail: {e}")
    
    return None
