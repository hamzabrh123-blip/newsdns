import requests
import re
import base64
import os
import logging
import gc # Garbage collector for RAM safety

logger = logging.getLogger(__name__)

# --- SIDEBAR LOGIC ---
def get_common_sidebar_data():
    try:
        from mynews.models import News
        return {
            "bazaar_sidebar": News.objects.filter(category="Market").order_by("-date")[:5],
            "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
            "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:10],
            "technology_sidebar": News.objects.filter(category="Technology").order_by("-date")[:3],
            "bollywood_sidebar": News.objects.filter(category="Bollywood").order_by("-date")[:3],
            "lucknow_up_sidebar": News.objects.filter(district='Lucknow').order_by("-date")[:10],
        }
    except Exception as e:
        logger.error(f"Sidebar Data Error: {e}")
        return {}

# --- IMGBB LOGIC ---
def upload_to_imgbb(image_field):
    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        logger.error("ImgBB API Key missing!")
        return None

    url = "https://api.imgbb.com/1/upload"
    try:
        # Image ko binary mode mein read karna (Memory bachaane ke liye)
        image_field.open()
        raw_data = image_field.read()
        image_data = base64.b64encode(raw_data)
        image_field.close()

        payload = {
            "key": api_key,
            "image": image_data,
        }
        
        # Requests ke time timeout ko 20-30 sec rakhna sahi hai
        response = requests.post(url, data=payload, timeout=25)
        
        # Memory saaf karna
        del raw_data
        del image_data
        gc.collect()

        if response.status_code == 200:
            return response.json()['data']['url']
        else:
            logger.error(f"ImgBB Response Fail: {response.text}")
            return None
    except Exception as e:
        logger.error(f"ImgBB Error: {e}")
        return None

# --- VIDEO ID EXTRACTION ---
def extract_video_id(url):
    if not url:
        return None
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None
