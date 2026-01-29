import requests
import base64
import os

def upload_to_imgbb(image_field):
    # API Key check
    api_key = os.environ.get("IMGBB_API_KEY")
    if not api_key:
        print("Error: IMGBB_API_KEY environment variable mein nahi mili!")
        return None

    url = "https://api.imgbb.com/1/upload"
    
    try:
        # Image ko sahi se read karna
        image_field.open() # File ko open karna zaroori hai
        image_data = base64.b64encode(image_field.read())
        image_field.close() # Kaam hone ke baad close karna achhi aadat hai
        
        payload = {
            "key": api_key,
            "image": image_data,
        }
        
        # Timeout add karna zaroori hai taaki server hang na ho
        response = requests.post(url, data=payload, timeout=30)
        json_data = response.json()
        
        if response.status_code == 200:
            # Direct image link return karega
            return json_data['data']['url']
        else:
            print(f"ImgBB API Error: {json_data.get('error', {}).get('message', 'Unknown Error')}")
            return None
            
    except Exception as e:
        print(f"Upload process failed: {e}")
        return None
