from django.urls import path
# Har file ko uske kaam ke hisaab se import kar rahe hain
from .views import home_views, content_views, seo_views

urlpatterns = [
    # --- HOME PAGE ---
    path("", home_views.home, name="home"),

    # --- API ---
    path("api/v1/fb-share-data/", content_views.fb_news_api, name='fb_api'),

    # --- NAYE SECTION PAGES (Strict Logic) ---
    path("desh/", home_views.national_view, name="national_page"),
    path("videsh/", home_views.world_view, name="world_page"),
    path("uttar-pradesh/", home_views.up_news_view, name="up_news_page"),
    path("manoranjan/", home_views.ent_view, name="ent_page"),

    # 1. Technology Fix
    path("technology/", home_views.district_news, {'district': 'Technology'}, name="technology_direct"),
    path("news/tech/", home_views.district_news, {'district': 'Technology'}, name="technology"),

    # 2. Universal Category Route
    path("category/<str:district>/", home_views.district_news, name="district_news"),

    # 3. Purane Names (For SEO Compatibility)
    path("news/national/", home_views.national_view, name="national_news"),
    path("news/international/", home_views.world_view, name="international_news"),
    path("news/int/", home_views.world_view, name="international"),
    path("news/sports/", home_views.district_news, {'district': 'Sports'}, name="sports"),
    path("news/bollywood/", home_views.ent_view, name="bollywood"),
    path("news/market/", home_views.district_news, {'district': 'Market'}, name="market"),

    # 4. Utilities & SEO
    path("robots.txt", seo_views.robots_txt, name="robots_txt"),
    path("sitemap.xml", seo_views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", seo_views.ads_txt, name="ads_txt"),
    path("privacy-policy/", seo_views.privacy_policy, name="privacy_policy"),
    path("about-us/", seo_views.about_us, name="about_us"),
    path("contact-us/", seo_views.contact_us, name="contact_us"),
    path("disclaimer/", seo_views.disclaimer, name="disclaimer"),

    # 5. Detail Page (Hamesha Last Mein)
    path("<str:url_city>/<slug:slug>/", content_views.news_detail, name="news_detail"),
]
