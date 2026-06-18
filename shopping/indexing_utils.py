import os
import json
from dotenv import load_dotenv  # 1. इसे इम्पोर्ट करना ज़रूरी है
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 2. ये कमांड .env फाइल को लोड करेगी (सिर्फ लोकल के लिए)
load_dotenv() 

def notify_google_indexing(url):
    SCOPES = ['https://www.googleapis.com/auth/indexing']
    
    # Render हो या Local, ये दोनों जगह से वेरिएबल उठा लेगा
    creds_json = os.environ.get('GOOGLE_JSON_CONTENT')
    
    if not creds_json:
        # अगर एनवायरमेंट वेरिएबल नहीं मिला, तो फाइल से लोड करेगा
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'service_account.json')
        
        with open(SERVICE_ACCOUNT_FILE, 'r', encoding='utf-8') as f:
            creds_dict = json.load(f)
    else:
        # अगर वेरिएबल मिल गया, तो उसे सीधे लोड कर लेगा
        creds_dict = json.loads(creds_json)
            
    # अब क्रेडेंशियल बनाना
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )
    
    service = build('indexing', 'v3', credentials=credentials)
    batch = {'url': url, 'type': 'URL_UPDATED'}
    return service.urlNotifications().publish(body=batch).execute()