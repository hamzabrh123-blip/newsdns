from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("national/", views.national_news, name="national_news"),
    path("technology/", views.technology, name="technology"),
    path("bollywood/", views.bollywood, name="bollywood"),
    path("international/", views.international_news, name="international_news"),
    path("district/<str:district>/", views.district_news, name="district_news"),
    
    # SEO & Legal Pages
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # ✅ न्यूज़ डिटेल: /lucknow/news-slug.html (सबसे बेस्ट SEO फॉर्मेट)
    path("<str:url_city>/<slug:slug>.html", views.news_detail, name="news_detail"),
    
    # ✅ ओल्ड न्यूज़ रीडायरेक्ट: अगर कोई पुरानी लिंक /news-slug/ पर क्लिक करे
    # इसे न्यूज़ डिटेल के नीचे ही रखें
    path("<slug:slug>/", views.old_news_redirect, name="old_news_redirect"),
]
