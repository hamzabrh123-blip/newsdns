from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # 1. Universal Category Route (Ise DETAIL se upar rakho taaki clash na ho)
    path("category/<str:district>/", views.district_news, name="district_news"),

    # 2. Sabhi Purane Names (Template Compatibility)
    path("news/national/", views.district_news, {'district': 'National'}, name="national_news"),
    path("news/international/", views.district_news, {'district': 'International'}, name="international_news"),
    path("news/int/", views.district_news, {'district': 'International'}, name="international"),
    path("news/tech/", views.district_news, {'district': 'Technology'}, name="technology"),
    path("news/sports/", views.district_news, {'district': 'Sports'}, name="sports"),
    path("news/bollywood/", views.district_news, {'district': 'Bollywood'}, name="bollywood"),
    path("news/market/", views.district_news, {'district': 'Market'}, name="market"),

    # 3. News Detail Page (Ise niche rakho kyunki ye sabse flexible hai)
    path("<str:url_city>/<slug:slug>/", views.news_detail, name="news_detail"),

    # 4. Utilities & SEO
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
]