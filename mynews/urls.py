from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # API for PC Script
    path("api/v1/fb-share-data/", views.fb_news_api, name='fb_api'),

    # --- NAYE SECTION PAGES (ALAG LOGIC WALE) ---
    path("desh/", views.national_view, name="national_page"),
    path("videsh/", views.world_view, name="world_page"),
    path("uttar-pradesh/", views.up_news_view, name="up_news_page"),
    path("manoranjan/", views.ent_view, name="ent_page"),

    # 1. Technology Fix
    path("technology/", views.district_news, {'district': 'Technology'}, name="technology_direct"),
    path("news/tech/", views.district_news, {'district': 'Technology'}, name="technology"),

    # 2. Universal Category Route
    path("category/<str:district>/", views.district_news, name="district_news"),

    # 3. Purane Names (For SEO Compatibility)
    path("news/national/", views.national_view, name="national_news"), # Ab ye naye view par jayega
    path("news/international/", views.world_view, name="international_news"),
    path("news/int/", views.world_view, name="international"),
    path("news/sports/", views.district_news, {'district': 'Sports'}, name="sports"),
    path("news/bollywood/", views.ent_view, name="bollywood"),
    path("news/market/", views.district_news, {'district': 'Market'}, name="market"),

    # 4. Utilities & SEO
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # 5. Detail Page (Hamesha Last Mein)
    path("<str:url_city>/<slug:slug>/", views.news_detail, name="news_detail"),
]
