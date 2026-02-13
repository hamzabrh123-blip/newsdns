import logging
from django.db.models import Q
from ..models import News
from ..constants import LOCATION_DATA

def published_news():
    return News.objects.filter(status__iexact="Published").order_by("-date")

def get_common_sidebar_data():
    published = published_news()
    return {
        "up_sidebar": published.filter(Q(category__icontains="up") | Q(district__isnull=False)).exclude(category__icontains="national")[:8],
        "world_sidebar": published.filter(Q(category__icontains="international") | Q(category__icontains="world"))[:5],
        "bazaar_sidebar": published.filter(category__icontains="market")[:5],
        "sports_sidebar": published.filter(category__icontains="sports")[:5],
        "dynamic_big_categories": [
            {"id": "National", "name": "देश"},
            {"id": "International", "name": "दुनिया"},
            {"id": "Sports", "name": "खेल"},
            {"id": "Market", "name": "बाज़ार"},
        ],
    }
