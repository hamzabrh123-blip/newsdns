import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def notify_google_indexing(url):
    SCOPES = ['https://www.googleapis.com/auth/indexing']
    
    # 1. पहले Render के एनवायरमेंट वेरिएबल से डेटा चेक करो
    creds_json = os.environ.get('GOOGLE_JSON_CONTENT')
    
    if creds_json:
        # अगर वेरिएबल मिला, तो सीधे JSON से लोड करो
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES
        )
    else:
        # अगर लोकल पीसी पर हो, तो फाइल से लोड करो
        SERVICE_ACCOUNT_FILE = 'service_account.json'
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
    
    service = build('indexing', 'v3', credentials=credentials)
    
    batch = {'url': url, 'type': 'URL_UPDATED'}
    return service.urlNotifications().publish(body=batch).execute()