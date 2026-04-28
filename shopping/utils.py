import requests
import base64
from django.conf import settings

def upload_to_imgbb(image_file):
    """
    इमेज को ImgBB पर अपलोड करता है और उसका डायरेक्ट URL वापस देता है।
    API Key को settings.py से IMGBB_API_KEY नाम से उठाता है।
    """
    # Settings से API Key प्राप्त करें
    api_key = getattr(settings, 'IMGBB_API_KEY', None)
    
    if not api_key:
        print("Upload Error: IMGBB_API_KEY is not defined in settings.py")
        return None

    url = "https://api.imgbb.com/1/upload"
    
    try:
        # फाइल पॉइंटर को शुरुआत में लाएं (ताकि पूरी इमेज पढ़ी जा सके)
        image_file.seek(0)
        
        # इमेज डेटा को बाइनरी से Base64 स्ट्रिंग में बदलें
        image_data = image_file.read()
        encoded_string = base64.b64encode(image_data)
        
        # API के लिए पेलोड तैयार करें
        payload = {
            "key": api_key,
            "image": encoded_string,
        }
        
        # ImgBB API को POST रिक्वेस्ट भेजें
        response = requests.post(url, data=payload)
        
        # अगर अपलोड सफल रहा (Status Code 200)
        if response.status_code == 200:
            json_response = response.json()
            # डायरेक्ट इमेज URL वापस भेजें
            return json_response['data']['url']
        else:
            print(f"ImgBB API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Upload Error: {e}")
    
    return None
