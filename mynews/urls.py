from django.urls import path, re_path
from django.views.generic.base import RedirectView
from . import views
from .feeds import LatestNewsFeed

urlpatterns = [
    # --- 1. HOME PAGE ---
    path("", views.home, name="home"),

    # --- 2. OLD BROKEN LINKS CLEANUP ---
    # पुराने फोल्डर्स (google, district, news-old आदि) को सीधा होमपेज भेजें
    re_path(r'^(google|district|news-old|old-post|archive)/.*$', RedirectView.as_view(url='/', permanent=True)),

    # किसी भी फाइल के अंत में .html, .php, .asp हो (अक्सर पुरानी साइट्स से आते हैं)
    re_path(r'.*\.(html|php|asp|aspx)$', RedirectView.as_view(url='/', permanent=True)),

    # कानपुर के पुराने नाम सुधारें
    re_path(r'^(category/)?(kanpur-nagar|kanpur-dehat)/?$', RedirectView.as_view(url='/category/kanpur/', permanent=True)),

    # पुराने बेकार कैटेगरी नाम जो अब नहीं हैं
    re_path(r'^(bollywood|sports|market|national|international|bahraich-gonda|gonda-news|azamgarh-news|balrampur-news|up-national)/?$', RedirectView.as_view(url='/', permanent=True)),

    # --- 3. API & UTILITIES ---
    path("api/v1/fb-share-data/", views.fb_news_api, name='fb_api'),
    path("feed/latest/", LatestNewsFeed(), name="news_feed"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),

    # --- 4. CATEGORIES & DISTRICTS ---
    path("technology/", views.district_news, {'district': 'Technology'}, name="technology_direct"),
    path("news/tech/", views.district_news, {'district': 'Technology'}, name="technology"),
    path("category/<str:district>/", views.district_news, name="district_news"),

    # Search Engine Compatibility
    path("news/national/", views.district_news, {'district': 'National'}, name="national_news"),
    path("news/international/", views.district_news, {'district': 'International'}, name="international_news"),
    path("news/sports/", views.district_news, {'district': 'Sports'}, name="sports"),
    path("news/bollywood/", views.district_news, {'district': 'Bollywood'}, name="bollywood"),
    path("news/market/", views.district_news, {'district': 'Market'}, name="market"),

    # --- 5. STATIC PAGES ---
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # --- 6. NEWS DETAIL (Main Logic) ---
    # यह सिर्फ तब चलेगा जब ऊपर के किसी रास्ते से मैच नहीं होगा
    path("<str:url_city>/<slug:slug>/", views.news_detail, name="news_detail"),

    # --- 7. THE MASTER CATCH-ALL REDIRECT (सबका इलाज) ---
    # अगर ऊपर का कोई भी रास्ता मैच नहीं हुआ, तो 404 देने के बजाय चुपचाप होमपेज भेज दो
    # यह रूल सबसे आखिर में होना अनिवार्य है!
    re_path(r'^.*$', RedirectView.as_view(url='/', permanent=True)),
]
