from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import News
from django.utils.feedgenerator import Rss201rev2Feed

class LatestNewsFeed(Feed):
    title = "Uttar World - ताज़ा समाचार"
    link = "/"
    description = "उत्तर प्रदेश और दुनिया की तमाम बड़ी खबरें।"

    # यह आपकी टॉप 20 ताज़ा खबरें उठाएगा
    def items(self):
        return News.objects.filter(status='Published').order_by('-date')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        # खबर का छोटा हिस्सा (डिस्क्रिप्शन के लिए)
        if item.content:
            return item.content[:200] + "..."
        return ""

    def item_link(self, item):
        # यहाँ अपनी news_detail वाली URL का नाम लिखें
        return reverse('news_detail', args=[item.url_city or 'news', item.slug])

    def item_pubdate(self, item):
        return item.date
