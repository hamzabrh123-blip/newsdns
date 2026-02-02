from django.urls import path
from .views import ( 
    home, national_news, technology, bollywood, international_news,
    market_news_view, district_news, robots_txt, sitemap_xml,
    ads_txt, privacy_policy, about_us, contact_us, disclaimer, 
    news_detail, fix_webp_image
)

urlpatterns = [
    path("", home, name="home"),
    path("national/", national_news, name="national_news"),
    path("technology/", technology, name="technology"),
    path("bollywood/", bollywood, name="bollywood"),
    path("international/", international_news, name="international_news"),
    path("market-news/", market_news_view, name="market_news"),

    path("fix-img/", fix_webp_image, name="fix_webp_image"),

    path("district/<str:district>/", district_news, name="district_news"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
    path("ads.txt", ads_txt, name="ads_txt"),
    path("privacy-policy/", privacy_policy, name="privacy_policy"),
    path("about-us/", about_us, name="about_us"),
    path("contact-us/", contact_us, name="contact_us"),
    path("disclaimer/", disclaimer, name="disclaimer"),

    # --- NEWS DETAIL FIX ---
    # Ye rasta city aur slug dono ke liye (lucknow/khabar-ki-link.html)
    path("<str:url_city>/<slug:slug>.html", news_detail, name="news_detail"),
    
    # Ye backup rasta (agar galti se city na ho tab bhi news khulegi)
    path("news/<slug:slug>.html", news_detail, name="news_detail_simple"),
]