# ---------------------------------------------------
# 1. CORE HELPERS & SIDEBAR
# ---------------------------------------------------
def published_news():
    return News.objects.filter(status__iexact="Published").order_by("-date")

def get_common_sidebar_data():
    published = published_news()
    
    # Fast filtering for Sidebar
    return {
        "up_sidebar": published.filter(Q(category__icontains="up") | Q(district__isnull=False)).exclude(category__icontains="national")[:8],
        "world_sidebar": published.filter(Q(category__icontains="international") | Q(category__icontains="world"))[:5],
        "bazaar_sidebar": published.filter(Q(category__icontains="market") | Q(category__icontains="business"))[:5],
        "sports_sidebar": published.filter(Q(category__icontains="sports"))[:5],
        "dynamic_big_categories": [
            {"id": "National", "name": "देश"},
            {"id": "International", "name": "दुनिया"},
            {"id": "Sports", "name": "खेल"},
            {"id": "Market", "name": "बाज़ार"},
        ],
    }
