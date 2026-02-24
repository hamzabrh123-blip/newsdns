from django.urls import path
from . import views
from .feeds import LatestNewsFeed

urlpatterns = [
    # 1. Static & Home
    path("", views.home, name="home"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),

    # 2. RSS Feeds
    path("feed/latest/", LatestNewsFeed(), name="news_feed"),

    # 3. API
    path("api/v1/fb-share-data/", views.fb_news_api, name='fb_api'),

    # 4. Fixed Categories (SEO Friendly)
    # Tip: Inhe model ke 'district' field se match hona chahiye exactly
    path("technology/", views.district_news, {'district': 'Technology'}, name="technology"),
    path("up-news/", views.district_news, {'district': 'UP-News'}, name="up_news_list"), # Dash use karein
    path("world/", views.district_news, {'district': 'International'}, name="world_news_list"),
    path("market/", views.district_news, {'district': 'Market'}, name="market_list"),
    path("sports/", views.district_news, {'district': 'Sports'}, name="sports_list"),

    # 5. Compatibility (Purane links na tootein isliye)
    path("news/national/", views.district_news, {'district': 'National'}, name="national_news"),
    path("news/international/", views.district_news, {'district': 'International'}, name="international_news"),
    path("news/sports/", views.district_news, {'district': 'Sports'}, name="sports_news"),
    path("news/bollywood/", views.district_news, {'district': 'Bollywood'}, name="bollywood"),
    path("news/market/", views.district_news, {'district': 'Market'}, name="market_news"),

    # 6. Dynamic Zila/District Route (uttarworld.com/zila/ballia/)
    path("zila/<str:district>/", views.district_news, name="district_news"),

    # 7. Static Pages
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # 8. NEWS DETAIL PAGE (Sabse Neeche - The Catch-All)
    # Ye pattern har us cheez ko pakad lega jo upar match nahi hui
    path("<str:url_city>/<slug:slug>/", views.news_detail, name="news_detail"),
]
