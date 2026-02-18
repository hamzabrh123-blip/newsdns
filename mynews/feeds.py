from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import News
from django.utils.feedgenerator import Rss201rev2Feed

# --- Media RSS Support (ताकि Dailyhunt फोटो उठा सके) ---
class ExtendedRssFeed(Rss201rev2Feed):
    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        if item.get('image_url'):
            # यह टैग Dailyhunt/Google News को फोटो का रास्ता बताता है
            handler.addQuickElement('enclosure', '', {
                'url': item['image_url'],
                'type': 'image/jpeg',
                'length': '1024',
            })

class LatestNewsFeed(Feed):
    feed_type = ExtendedRssFeed
    title = "Uttar World - ताज़ा समाचार"
    link = "/"
    description = "उत्तर प्रदेश और दुनिया की तमाम बड़ी खबरें।"

    # टॉप 20 ताज़ा खबरें (Published वाली)
    def items(self):
        return News.objects.filter(status='Published').order_by('-date')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.content:
            # RSS के लिए थोड़ा लंबा डिस्क्रिप्शन (300 chars) बेहतर है
            return item.content[:300] + "..."
        return ""

    # आपका URL Structure: <str:url_city>/<slug:slug>/
    def item_link(self, item):
        city = item.url_city if item.url_city else 'news'
        return reverse('news_detail', args=[city, item.slug])

    def item_pubdate(self, item):
        return item.date

    # इमेजेस को फीड में शामिल करने के लिए
    def item_extra_kwargs(self, item):
        # पहले ImgBB (image_url) चेक करेगा, नहीं तो लोकल इमेज
        img = item.image_url if item.image_url else (item.image.url if item.image else None)
        return {'image_url': img}
