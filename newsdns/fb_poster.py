import facebook
import requests
import time

# --- CONFIGURATION ---
TOKEN = 'EAAKixQCgB9gBQqHyzRm4ab0bMZAWwq5xCD88S42hpPmCcdbAK6JHGyp9ncVlUifB65jfFVeB2ePMU2bYc653FBnjC2sOH1pSx9nCZB1TMnigNLB00stZAOYGOGOvuMDO5WKx5QiiZBmLrNIHMGA4zL6o0oSIf01OYxQJOmiJFhCvVvSgEyTujXAJXxHEMZBAiP03PSXIZD'
FB_PAGE_ID = '108286920828619'  
FB_GROUP_1_ID = '777785508987814'

API_URL = "https://uttarworld.com/api/v1/fb-share-data/"

def bulk_power_poster():
    try:
        # Facebook Graph API setup
        graph = facebook.GraphAPI(access_token=TOKEN)
        
        print(f"🔗 {API_URL} se bulk data kheencha raha hai...")
        response = requests.get(API_URL)
        news_list = response.json()

        if not news_list:
            print("❌ API khali hai! Views.py check karo (status='Published' hona chahiye).")
            return

        print(f"🔥 Dhamaka! Total {len(news_list)} news mili hain. Posting shuru...")

        for news in news_list:
            msg = f"🔴 {news['title']}\n\nपूरी खबर यहाँ पढ़ें: {news['url']}"
            
            try:
                # 1. Page par post (Variable name fixed)
                print(f"📤 Posting to Page: {news['title']}...")
                graph.put_object(
                    parent_object=FB_PAGE_ID, 
                    connection_name='feed', 
                    message=msg, 
                    link=news['url']
                )
                print(f"✅ Page Success!")

                # 2. Group par post (Aapne ID di hai toh use karte hain)
                try:
                    print(f"👥 Posting to Group...")
                    graph.put_object(
                        parent_object=FB_GROUP_1_ID,
                        connection_name='feed',
                        message=msg,
                        link=news['url']
                    )
                    print(f"✅ Group Success!")
                except Exception as ge:
                    print(f"⚠️ Group post nahi hui (Permissions check karein): {ge}")
                
                # Gap to avoid spam blocks
                print("⌛ 30 second ka wait agali news ke liye...")
                time.sleep(30) 

            except Exception as e:
                print(f"❌ Is news mein error aaya: {e}")

    except Exception as e:
        print(f"⚠️ Connection Error: {e}")

if __name__ == "__main__":
    bulk_power_poster()
    print("🏁 Bulk Force Posting khatam!")