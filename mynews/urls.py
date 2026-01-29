from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("national/", views.national_news, name="national_news"),
    path("technology/", views.technology, name="technology"),
    path("bollywood/", views.bollywood, name="bollywood"),
    path("international/", views.international_news, name="international_news"),
    
    # ✅ Market News Link (Ise District se upar rakha hai taaki clash na ho)
    path("market-news/", views.market_news_view, name="market_news"),

    path("district/<str:district>/", views.district_news, name="district_news"),
    
    # SEO & Legal Pages
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # ✅ न्यूज़ डिटेल: /city/news-slug.html (The Final SEO Structure)
    path("<str:url_city>/<slug:slug>.html", views.news_detail, name="news_detail"),
]
