from django.urls import path, re_path
from django.views.generic.base import RedirectView
from . import views
from .feeds import LatestNewsFeed

urlpatterns = [
    # --- 1. HOME PAGE ---
    path("", views.home, name="home"),

    # --- 2. THE ULTIMATE CLEANUP (शातिर 404 एरर्स का गेम यहाँ खत्म) ---
    
    # A. 'district/' और 'google/' वाले सभी पुराने रास्तों को होमपेज पर भेजें
    re_path(r'^(google|district)/.*$', RedirectView.as_view(url='/', permanent=True)),

    # B. किसी भी फाइल के अंत में .html हो तो उसे दफन करो
    re_path(r'.*\.html$', RedirectView.as_view(url='/', permanent=True)),

    # C. सीधे नाम वाले लिंक्स (bollywood/, sports/ आदि) और पुराने जिला नाम
    re_path(r'^(category/)?(kanpur-nagar|kanpur-dehat)/?$', RedirectView.as_view(url='/category/kanpur/', permanent=True)),
    # यह नियम बिना 'news/' या 'category/' वाले सीधे लिंक्स को पकड़ लेगा
    re_path(r'^(bollywood|sports|market|national|international|bahraich-gonda|gonda-news|azamgarh-news|balrampur-news|up-national)/?$', RedirectView.as_view(url='/', permanent=True)),

    # --- 3. API & SCRIPTS ---
    path("api/v1/fb-share-data/", views.fb_news_api, name='fb_api'),

    # --- 4. CATEGORIES & DISTRICTS (New Working Structure) ---
    path("technology/", views.district_news, {'district': 'Technology'}, name="technology_direct"),
    path("news/tech/", views.district_news, {'district': 'Technology'}, name="technology"),
    
    # Universal Category Route
    path("category/<str:district>/", views.district_news, name="district_news"),

    # Search Engine Compatibility Paths (news/ के साथ)
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

    # --- 6. NEWS DETAIL PAGE (Hamesha Sabse Neeche) ---
    # यह नियम सबसे आखिरी गार्ड है
    path("<str:url_city>/<slug:slug>/", views.news_detail, name="news_detail"),
]
