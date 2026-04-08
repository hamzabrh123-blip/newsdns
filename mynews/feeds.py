from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import News
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import strip_tags

# --- Media & Video RSS Support ---
class ExtendedRssFeed(Rss201rev2Feed):
    def rss_attributes(self):
        attrs = super().rss_attributes()
        # यहाँ Media Namespace जोड़ना ज़रूरी है ताकि वीडियो और फोटो सही से रीड हों
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
            })

        # 2. वीडियो सपोर्ट (Video Logic)
        if item.get('video_url'):
            video_url = item['video_url']
            # YouTube ID निकालकर Embed URL बनाना
            video_id = ""
            if "v=" in video_url: video_id = video_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in video_url: video_id = video_url.split("youtu.be/")[1].split("?")[0]
            
            if video_id:
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                # Media player और content टैग्स डेलीहंट जैसे एप्स के लिए
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
        return News.objects.filter(status='Published').order_by('-date')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.content:
            # RSS के लिए साफ़ टेक्स्ट (HTML टैग्स हटाकर)
            return strip_tags(item.content[:400]) + "..."
        return ""

    def item_link(self, item):
        city = item.url_city.lower() if item.url_city else 'news'
        return reverse('news_detail', args=[city, item.slug])

    def item_pubdate(self, item):
        return item.date

    # एक्स्ट्रा डेटा (फोटो और वीडियो) को फीड में भेजने के लिए
    def item_extra_kwargs(self, item):
        # फोटो का चुनाव
        img = item.image_url if item.image_url else (item.image.url if item.image else None)
        # वीडियो का चुनाव
        video = item.youtube_url if item.youtube_url else None
        
        return {
            'image_url': img,
            'video_url': video
        }
