import requests
import base64

def upload_to_imgbb(image_file):
    # तेरी जादुई चाबी यहाँ फिट कर दी है
    api_key = "b853b0baf2f11d6514d3c4024293a0fd" 
    url = "https://api.imgbb.com/1/upload"
    
    try:
        # इमेज को बाइनरी से बेस64 में बदलना
        image_file.seek(0) # फाइल पॉइंटर को शुरू में लाएं
        encoded_string = base64.b64encode(image_file.read())
        
        payload = {
            "key": api_key,
            "image": encoded_string,
        }
        
        response = requests.post(url, payload)
        if response.status_code == 200:
            return response.json()['data']['url'] # यह सीधा इमेज लिंक देगा
    except Exception as e:
        print(f"Upload Error: {e}")
    
    return None