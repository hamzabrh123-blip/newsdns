import requests
import re
import base64
import os
import logging
import gc
import io
from PIL import Image
import pillow_avif  # AVIF सपोर्ट के लिए ज़रूरी
from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)

# --- 1. SIDEBAR LOGIC ---
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

# --- 2. IMAGE PROCESSING & IMGBB (RAM OPTIMIZED + AVIF) ---
def process_and_upload_to_imgbb(instance):
    """
    AVIF/WebP को हैंडल करता है, वॉटरमार्क लगाता है और 
    512MB RAM के लिए मेमोरी क्लीनअप करता है।
    """
    # instance.image चेक करें (News या NewsImage मॉडल के लिए)
    image_field = getattr(instance, 'image', None)
    if not image_field or (hasattr(instance, 'image_url') and instance.image_url):
        return None

    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        logger.warning("IMGBB_API_KEY missing in environment")
        return None

    try:
        # RAM बचाने के लिए BytesIO का उपयोग
        img_data = image_field.read()
        img = Image.open(io.BytesIO(img_data))

        # AVIF/WebP/PNG को RGB में बदलें (ताकि वॉटरमार्क और JPEG सेव हो सके)
        if img.mode in ("RGBA", "P", "LA") or "avif" in str(img.format).lower():
            img = img.convert("RGB")
        
        # 512MB RAM के लिए इमेज रिसाइज़ (1000px चौड़ाई काफी है)
        img.thumbnail((1000, 1000), Image.Resampling.LANCZOS)

        # --- Watermark Logic ---
        try:
            w_path = os.path.join(settings.BASE_DIR, 'mynews', 'static', 'watermark.png')
            if os.path.exists(w_path):
                with Image.open(w_path).convert("RGBA") as w_img:
                    # वॉटरमार्क साइज़: मेन इमेज का 20%
                    w_img.thumbnail((img.width // 5, img.height // 5))
                    # Bottom Right पोजीशन
                    pos = (img.width - w_img.width - 15, img.height - w_img.height - 15)
                    img.paste(w_img, pos, w_img)
        except Exception as we:
            logger.error(f"Watermark Error: {we}")

        # --- Memory Optimized Saving ---
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=80, optimize=True)
        base64_image = base64.b64encode(output.getvalue())

        # भारी डेटा को तुरंत डिलीट करें
        img.close()
        del img_data
        gc.collect()

        # ImgBB पर अपलोड
        payload = {"key": api_key, "image": base64_image}
        response = requests.post("https://api.imgbb.com/1/upload", data=payload, timeout=25)

        if response.status_code == 200:
            return response.json()['data']['url']
        
        return None

    except Exception as e:
        logger.error(f"Image Processing/ImgBB Error: {e}")
        return None
    finally:
        gc.collect()

# --- 3. FACEBOOK AUTO-POST ---
def post_to_facebook(instance):
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_ids = [os.environ.get('FB_PAGE_ID'), os.environ.get('FB_PAGE_2_ID')]
    group_id = os.environ.get('FB_GROUP_1_ID') 

    if not access_token:
        logger.error("FB Access Token missing")
        return False

    try:
        # Dynamic URL Structure
        city_slug = instance.url_city if instance.url_city else "news"
        news_link = f"https://uttarworld.com/{city_slug}/{instance.slug}/"
        
        msg = f"{instance.title}\n\nपूरी खबर यहाँ पढ़ें: {news_link}\n\n#UttarWorld #UPNews #{instance.district}"
        
        # API Version v21.0 (Latest)
        api_version = "v21.0"
        
        if instance.image_url:
            payload = {'url': instance.image_url, 'caption': msg, 'access_token': access_token}
            suffix = "/photos"
        else:
            payload = {'message': msg, 'link': news_link, 'access_token': access_token}
            suffix = "/feed"

        # 1. Pages पर पोस्ट करें
        for p_id in page_ids:
            if p_id:
                requests.post(f"https://graph.facebook.com/{api_version}/{p_id}{suffix}", data=payload, timeout=20)

        # 2. Group पर पोस्ट करें
        if group_id:
            requests.post(f"https://graph.facebook.com/{api_version}/{group_id}{suffix}", data=payload, timeout=20)

        return True
    except Exception as e:
        logger.error(f"FB Auto-Post Error: {e}")
        return False

# --- 4. UTILITY FUNCTIONS ---
def extract_video_id(url):
    if not url: 
        return None
    # यह Regex सबसे पावरफुल है, जो हर तरह के YouTube लिंक से 11 अक्षरों की ID निकालता है
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url)
    if match:
        return match.group(1) # यही वो dQw4w9WgXcQ निकालेगा
    return None
