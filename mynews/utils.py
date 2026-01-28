import requests
import base64
import os

def upload_to_imgbb(image_file):
    # API Key Render ke Environment variables se lega
    # Agar Render pe key nahi mili, toh ye None return karega (Safe approach)
    api_key = os.environ.get("IMGBB_API_KEY")
    
    if not api_key:
        print("Error: IMGBB_API_KEY nahi mili. Render settings check karein.")
        return None

    url = "https://api.imgbb.com/1/upload"
    
    try:
        # Image ko base64 format mein convert karna
        image_file.seek(0) # File pointer ko shuruat mein le jane ke liye
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