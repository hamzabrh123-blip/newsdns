import os
import requests
import base64
import io
import logging
import gc
import re
from PIL import Image

# AVIF सपोर्ट के लिए
try:
    import pillow_avif
except ImportError:
    pass

from django.conf import settings
from django.apps import apps
from django.contrib.staticfiles import finders

logger = logging.getLogger(__name__)

# --- 1. SIDEBAR LOGIC (News के लिए) ---
def get_common_sidebar_data():
    try:
        News = apps.get_model('mynews', 'News') 
        return {
            "bazaar_sidebar": News.objects.filter(category="Market", status='Published').order_by("-date")[:5],
            "bharat_sidebar": News.objects.filter(category="National", status='Published').order_by("-date")[:10],
            "duniya_sidebar": News.objects.filter(category="International", status='Published').order_by("-date")[:10],
            "technology_sidebar": News.objects.filter(category="Technology", status='Published').order_by("-date")[:3],
            "bollywood_sidebar": News.objects.filter(category="Bollywood", status='Published').order_by("-date")[:3],
            "lucknow_up_sidebar": News.objects.filter(district='Lucknow', status='Published').order_by("-date")[:10],
        }
    except Exception as e:
        logger.error(f"Sidebar Data Error: {e}")
        return {}

# --- 2. UNIVERSAL IMAGE ENGINE (Enhanced News + Shopping) ---
def process_and_upload_to_imgbb(instance, is_shop=False):
    """
    is_shop=True होने पर शॉपिंग वाला लोगो उठाएगा।
    is_shop=False (Default) होने पर न्यूज़ वाला लोगो उठाएगा।
    """
    # 1. डायनामिक फील्ड चेक
    image_field = getattr(instance, 'image', None) or getattr(instance, 'main_image', None)
    
    if not image_field:
        return None

    # 2. API Key चेक
    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        logger.error("Bhai, Render me IMGBB_API_KEY nahi mili!")
        return None

    try:
        # 3. Image Loading
        image_field.seek(0)
        img = Image.open(io.BytesIO(image_field.read()))
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # --- वॉटरमार्क लॉजिक (News vs Shopping) ---
        if is_shop:
            # शॉपिंग के लिए स्पेसिफिक लोगो पाथ
            logo_path = finders.find('images/uttarworld-shopping-icon.png')
            logger.info("Attempting to apply Shopping Watermark...")
        else:
            # न्यूज़ के लिए पुराना वाला वॉटरमार्क
            logo_path = finders.find('watermark.png')
            logger.info("Attempting to apply News Watermark...")
        
        if logo_path and os.path.exists(logo_path):
            with Image.open(logo_path).convert("RGBA") as logo:
                # शॉपिंग के लिए थोड़ा छोटा (15%) न्यूज़ के लिए (18%)
                ratio = 0.15 if is_shop else 0.18
                logo_w = int(img.width * ratio)
                logo_h = int(logo.height * (logo_w / logo.width))
                logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                
                # Bottom-Right पोजीशन
                pos = (img.width - logo_w - 20, img.height - logo_h - 20)
                img.paste(logo, pos, logo)
                logger.info(f"{'Shopping' if is_shop else 'News'} Watermark applied.")
        else:
            logger.warning(f"Bhai Logo file nahi mili: {logo_path}")

        # 4. Optimization & WebP Conversion
        img = img.convert("RGB")
        if img.width > 1200:
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format='WEBP', quality=75, optimize=True)
        base64_image = base64.b64encode(output.getvalue())

        # 5. ImgBB POST Request
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": base64_image},
            timeout=30
        )

        # RAM Clean up
        img.close()
        gc.collect()

        if response.status_code == 200:
            new_url = response.json()['data']['url']
            logger.info(f"Upload Success: {new_url}")
            return new_url
        
        logger.error(f"ImgBB Fail: {response.text}")
        return None

    except Exception as e:
        logger.error(f"Fatal Processing Error: {e}")
        return None
    finally:
        gc.collect()

# --- 3. FACEBOOK AUTO-POST ---
def post_to_facebook(instance):
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_ids = [os.environ.get('FB_PAGE_ID'), os.environ.get('FB_PAGE_2_ID')]
    group_id = os.environ.get('FB_GROUP_1_ID') 

    if not access_token:
        return False

    try:
        city_slug = getattr(instance, 'url_city', 'news')
        link_base = "https://uttarworld.com"
        
        news_link = f"{link_base}/{city_slug}/{instance.slug}/"
        title = getattr(instance, 'title', 'Uttar World Update')
        district = getattr(instance, 'district', 'UP')
        
        msg = f"{title}\n\nपूरी जानकारी यहाँ पढ़ें: {news_link}\n\n#UttarWorld #UPNews #{district}"
        
        img_url = getattr(instance, 'image_url', None) or getattr(instance, 'main_image_url', None)
        
        if img_url:
            payload = {'url': img_url, 'caption': msg, 'access_token': access_token}
            endpoint = "photos"
        else:
            payload = {'message': msg, 'link': news_link, 'access_token': access_token}
            endpoint = "feed"

        for p_id in page_ids:
            if p_id:
                requests.post(f"https://graph.facebook.com/v21.0/{p_id}/{endpoint}", data=payload, timeout=20)

        if group_id:
            requests.post(f"https://graph.facebook.com/v21.0/{group_id}/{endpoint}", data=payload, timeout=20)

        return True
    except Exception as e:
        logger.error(f"FB Post Error: {e}")
        return False

# Compatibility Alias
def upload_to_imgbb(instance):
    """
    यह पुराने कोड के लिए है, ताकि एरर न आए।
    """
    return process_and_upload_to_imgbb(instance)