import requests
import base64
import io
import os
import logging
import gc
from PIL import Image
try:
    import pillow_avif
except ImportError:
    pass
from django.conf import settings
from django.apps import apps
from django.contrib.staticfiles import finders

logger = logging.getLogger(__name__)

# --- 1. SIDEBAR LOGIC (No Change) ---
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

# --- 2. UNIVERSAL IMAGE ENGINE (With Logo & ImgBB) ---
def process_and_upload_to_imgbb(instance):
    """
    यह फंक्शन News, NewsImage, और Shopping के सभी मॉडल्स के लिए काम करेगा।
    """
    # पक्का करें कि इमेज फील्ड मौजूद है (Shopping में 'main_image' या 'image' हो सकता है)
    image_field = getattr(instance, 'image', None) or getattr(instance, 'main_image', None)
    
    if not image_field:
        return None

    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        logger.error("CRITICAL: IMGBB_API_KEY not found in Environment!")
        return None

    try:
        # 1. Open Image with RAM control
        image_field.seek(0)
        img = Image.open(io.BytesIO(image_field.read()))
        
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 2. Watermark Logic (Static based)
        # न्यूज़ के लिए 'watermark.png' और शॉपिंग के लिए 'uttarworld-shopping-icon.png'
        # हम दोनों को चेक कर लेंगे
        logo_path = finders.find('watermark.png') or finders.find('images/uttarworld-shopping-icon.png')
        
        if logo_path and os.path.exists(logo_path):
            with Image.open(logo_path).convert("RGBA") as logo:
                # Logo size: 18% of main image width
                logo_w = int(img.width * 0.18)
                logo_h = int(logo.height * (logo_w / logo.width))
                logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                
                # Position: Bottom-Right
                pos = (img.width - logo_w - 20, img.height - logo_h - 20)
                img.paste(logo, pos, logo)
                logger.info("✅ Watermark applied successfully.")

        # 3. Memory Optimization & WebP Conversion
        img = img.convert("RGB")
        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS) # High quality but small size
        
        output = io.BytesIO()
        img.save(output, format='WEBP', quality=80, optimize=True)
        base64_image = base64.b64encode(output.getvalue())

        # Clean up RAM
        img.close()
        gc.collect()

        # 4. ImgBB Upload
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": api_key, "image": base64_image},
            timeout=30
        )

        if response.status_code == 200:
            new_url = response.json()['data']['url']
            logger.info(f"🔥 Upload Success: {new_url}")
            return new_url
        
        logger.error(f"❌ ImgBB Fail: {response.text}")
        return None

    except Exception as e:
        logger.error(f"💥 Fatal Processing Error: {e}")
        return None
    finally:
        gc.collect()

# --- 3. FACEBOOK AUTO-POST (Optimized) ---
def post_to_facebook(instance):
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_ids = [os.environ.get('FB_PAGE_ID'), os.environ.get('FB_PAGE_2_ID')]
    group_id = os.environ.get('FB_GROUP_1_ID') 

    if not access_token:
        return False

    try:
        city_slug = getattr(instance, 'url_city', 'news')
        # News और Product दोनों के लिए लिंक सपोर्ट
        link_base = "https://uttarworld.com"
        news_link = f"{link_base}/{city_slug}/{instance.slug}/"
        
        title = getattr(instance, 'title', 'Uttar World News')
        district = getattr(instance, 'district', 'UP')
        
        msg = f"{title}\n\nपूरी खबर यहाँ पढ़ें: {news_link}\n\n#UttarWorld #UPNews #{district}"
        
        # Image URL logic
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

# Alias for compatibility (ताकि shopping और news दोनों जगह काम करे)
def upload_to_imgbb(image_file_or_instance):
    # अगर सीधा मॉडल इंस्टेंस पास हुआ है
    if hasattr(image_file_or_instance, 'save'):
        return process_and_upload_to_imgbb(image_file_or_instance)
    # यह सिर्फ बैकअप के लिए है
    return None
