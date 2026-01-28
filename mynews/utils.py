import requests
import base64
import os

def upload_to_imgbb(image_file):
    # API Key Render ke Environment variables se lega
    api_key = os.environ.get("IMGBB_API_KEY", "d0528bc96d36a90b0cfbac9227174e41")
    url = "https://api.imgbb.com/1/upload"
    
    try:
        # Image ko base64 format mein convert karna
        image_data = base64.b64encode(image_file.read())
        
        data = {
            "key": api_key,
            "image": image_data,
        }
        
        response = requests.post(url, data=data)
        json_data = response.json()
        
        if response.status_code == 200:
            return json_data['data']['url'] # Direct image link
        else:
            print("ImgBB Error:", json_data)
            return None
    except Exception as e:
        print("Upload failed:", e)
        return None