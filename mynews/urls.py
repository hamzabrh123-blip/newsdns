from django.urls import path
from . import views

urlpatterns = [
    # --- Home Page ---
    path("", views.home, name="home"),

    # --- API for PC Script ---
    path("api/v1/fb-share-data/", views.fb_news_api, name='fb_api'),

    # --- Category Routes (Direct) ---
    path("technology/", views.district_news, {'district': 'Technology'}, name="technology_direct"),
    path("UP-News/", views.district_news, {'district': 'UP News'}, name="up_news_list"),
    path("Int-MiddleEast/", views.district_news, {'district': 'International'}, name="world_news_list"),
    path("Market/", views.district_news, {'district': 'Market'}, name="market_list"),
    path("Sports/", views.district_news, {'district': 'Sports'}, name="sports_list"),

    # --- Compatibility Routes ---
    path("news/national/", views.district_news, {'district': 'National'}, name="national_news"),
    path("news/international/", views.district_news, {'district': 'International'}, name="international_news"),
    path("news/sports/", views.district_news, {'district': 'Sports'}, name="sports"),
    path("news/bollywood/", views.district_news, {'district': 'Bollywood'}, name="bollywood"),
    path("news/market/", views.district_news, {'district': 'Market'}, name="market"),

    # --- Universal Category Route ---
    path("category/<str:district>/", views.district_news, name="district_news"),

    # --- Utilities & SEO ---
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # --- Detail Page (Must be at the bottom) ---
    path("<str:url_city>/<slug:slug>/", views.news_detail, name="news_detail"),
]
