from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import News
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import strip_tags

# --- Media & Video RSS Support (Extended) ---
class ExtendedRssFeed(Rss201rev2Feed):
    def rss_attributes(self):
        attrs = super().rss_attributes()
        # Media Namespace: फोटो और वीडियो रेंडरिंग के लिए ज़रूरी
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        return attrs

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        
        # 1. फोटो (Enclosure & Media Content)
        if item.get('image_url'):
            handler.addQuickElement('enclosure', '', {
                'url': item['image_url'],
                'type': 'image/jpeg',
                'length': '1024',
            })
            handler.addQuickElement('media:content', '', {
                'url': item['image_url'],
                'medium': 'image',
                'title': item.get('caption', ''),  # यहाँ कैप्शन/ALT टेक्स्ट जाएगा
            })

        # 2. वीडियो सपोर्ट (YouTube Embed Logic)
        if item.get('video_url'):
            video_url = item['video_url']
            video_id = ""
            if "v=" in video_url: 
                video_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url: 
                video_id = video_url.split("youtu.be/")[1].split("?")[0]
            
            if video_id:
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                handler.addQuickElement('media:content', '', {
                    'url': embed_url,
                    'medium': 'video',
                    'type': 'text/html',
                })
                handler.addQuickElement('media:player', '', {'url': embed_url})

class LatestNewsFeed(Feed):
    feed_type = ExtendedRssFeed
    title = "Uttar World - ताज़ा समाचार"
    link = "/"
    description = "उत्तर प्रदेश और दुनिया की तमाम बड़ी खबरें।"

    def items(self):
        # संख्या बढ़ाकर 50 कर दी है ताकि एग्रीगेटर्स को पर्याप्त डेटा मिले
        return News.objects.filter(status='Published').order_by('-date')[:50]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.content:
            # HTML हटाकर साफ़ टेक्स्ट और लम्बाई थोड़ी बढ़ाई है (SEO के लिए अच्छा है)
            return strip_tags(item.content[:500]) + "..."
        return ""

    def item_link(self, item):
        # SEO फ्रेंडली यूआरएल स्ट्रक्चर
        city = item.url_city.lower() if item.url_city else 'news'
        return reverse('news_detail', args=[city, item.slug])

    def item_pubdate(self, item):
        return item.date

    def item_extra_kwargs(self, item):
        # फोटो यूआरएल लॉजिक
        img = item.image_url if item.image_url else (item.image.url if item.image else None)
        # वीडियो यूआरएल
        video = item.youtube_url if item.youtube_url else None
        # कैप्शन लॉजिक: अगर कैप्शन नहीं है तो टाइटल को ही कैप्शन मानेंगे (ALT Fix)
        caption = item.image_caption if item.image_caption else item.title
        
        return {
            'image_url': img,
            'video_url': video,
            'caption': caption
        }
