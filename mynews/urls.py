from django.urls import path
from . import views
from django.shortcuts import redirect, get_object_or_404
from .models import News

# ✅ पुराने वायरल न्यूज़ लिंक को नए .html फॉर्मेट पर भेजने के लिए फंक्शन
def old_news_redirect(request, slug):
    # यह सिर्फ slug वाले लिंक को पकड़ेगा और उसे /city/slug.html पर भेज देगा
    news = get_object_or_404(News, slug=slug)
    return redirect(f'/{news.url_city}/{news.slug}.html', permanent=True)

urlpatterns = [
    # ===== CORE PAGES (No Change) =====
    path("", views.home, name="home"),
    path("national/", views.national_news, name="national_news"),
    path("technology/", views.technology, name="technology"),
    path("bollywood/", views.bollywood, name="bollywood"),
    path("international/", views.international_news, name="international_news"),
    
    # ज़िलों के पुराने पेज (बिल्कुल सुरक्षित हैं)
    path("district/<str:district>/", views.district_news, name="district_news"),

    # ===== SEO / SYSTEM FILES =====
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),

    # ===== ADSENSE IMPORTANT PAGES =====
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # ===== ✅ NEW NEWS DETAIL (District/Slug.html) =====
    # अब न्यूज़ का लिंक ऐसे खुलेगा: halchal.onrender.com/bahraich/khabar.html
    path("<str:url_city>/<slug:slug>.html", views.news_detail, name="news_detail"),

    # ===== ✅ OLD NEWS REDIRECT (Hamesha Last Mein) =====
    # अगर कोई पुराने बिना .html वाले लिंक पर आएगा, तो यह उसे नए पर भेज देगा
    path("<slug:slug>/", old_news_redirect),
]
