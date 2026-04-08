from django.urls import path, re_path
from django.views.generic.base import RedirectView
from . import views
from .feeds import LatestNewsFeed

urlpatterns = [
    # --- 1. HOME PAGE ---
    path("", views.home, name="home"),

    # --- 2. THE "CLEANUP" REDIRECTS (इन्हें टॉप पर रखना अनिवार्य है) ---
    
    # A. 'district/' वाले पुराने रास्तों को होमपेज पर भेजें (जो अभी एरर दे रहा था)
    re_path(r'^district/.*$', RedirectView.as_view(url='/', permanent=True)),

    # B. पुरानी /google/ वाली कैटेगरी को होमपेज पर भेजें
    re_path(r'^google/.*$', RedirectView.as_view(url='/', permanent=True)),

    # C. किसी भी यूआरएल के अंत में .html हो (जैसे news-title.html) तो उसे होमपेज पर भेजें
    re_path(r'.*\.html$', RedirectView.as_view(url='/', permanent=True)),

    # D. पुराने जिला/कैटेगरी लिंक्स (जैसे bahraich-gonda, gonda-news आदि)
    # यहाँ आप अपनी पुरानी कैटेगरी के नाम पाइप | लगाकर जोड़ सकते हैं
    re_path(r'^(bahraich-gonda|gonda-news|azamgarh-news|balrampur-news|up-national)/.*$', RedirectView.as_view(url='/', permanent=True)),

    # --- 3. API & SCRIPTS ---
    path("api/v1/fb-share-data/", views.fb_news_api, name='fb_api'),

    # --- 4. CATEGORIES & DISTRICTS (New Structure) ---
    path("technology/", views.district_news, {'district': 'Technology'}, name="technology_direct"),
    path("news/tech/", views.district_news, {'district': 'Technology'}, name="technology"),
    
    # Universal Category Route (e.g., /category/business/)
    path("category/<str:district>/", views.district_news, name="district_news"),

    # Search Engine Compatibility Paths
    path("news/national/", views.district_news, {'district': 'National'}, name="national_news"),
    path("news/international/", views.district_news, {'district': 'International'}, name="international_news"),
    path("news/int/", views.district_news, {'district': 'International'}, name="international"),
    path("news/sports/", views.district_news, {'district': 'Sports'}, name="sports"),
    path("news/bollywood/", views.district_news, {'district': 'Bollywood'}, name="bollywood"),
    path("news/market/", views.district_news, {'district': 'Market'}, name="market"),

    # --- 5. UTILITIES & SEO ---
    path("feed/latest/", LatestNewsFeed(), name="news_feed"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # --- 6. NEWS DETAIL PAGE (Hamesha Last Mein) ---
    # यह नियम सबसे नीचे है ताकि ऊपर के रिडायरेक्ट पहले अपना काम कर सकें
    path("<str:url_city>/<slug:slug>/", views.news_detail, name="news_detail"),
]
