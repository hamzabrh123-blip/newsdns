from django.urls import path
from . import views
from .feeds import LatestNewsFeed

urlpatterns = [
    # 1. API 
    path("api/v1/fb-share-data/", views.fb_news_api, name='fb_api'),

    # 2. Technology (Iska naam wapas 'technology' kar diya hai taaki error na aaye)
    path("technology/", views.district_news, {'district': 'Technology'}, name="technology"),
    path("news/tech/", views.district_news, {'district': 'Technology'}, name="technology_old"),

    # 3. Universal Category Route
    path("category/<str:district>/", views.district_news, name="district_news"),

    # 4. Purane Names (Compatibility)
    path("national/", views.district_news, {'district': 'National'}, name="national_news"),
    path("international/", views.district_news, {'district': 'International'}, name="international_news"),
    path("sports/", views.district_news, {'district': 'Sports'}, name="sports"),
    path("bollywood/", views.district_news, {'district': 'Bollywood'}, name="bollywood"),
    path("market/", views.district_news, {'district': 'Market'}, name="market"),

    # 5. Utilities & SEO
    path("feed/latest/", LatestNewsFeed(), name="news_feed"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # 6. News Detail (Iske aage 'n/' laga diya hai taaki Shopping se na takraye)
    # Ab link uttarworld.com/n/lucknow/slug jaisa hoga
    path("n/<str:url_city>/<slug:slug>/", views.news_detail, name="news_detail"),

    # 7. Default Home (Sabse neeche)
    path("", views.home, name="home"),
]
