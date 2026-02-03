from django.urls import path
from . import views # Isse code saaf rehta hai

urlpatterns = [
    # 1. Home Page
    path("", views.home, name="home"),

    # 2. THE BIG CONTROLLER (Universal Route)
    # Ab yahi ek rasta National, International, Sports, sab handle karega
    # Example: /national/, /sports/, /int-middleeast/ sab isi par jayenge
    path("<str:district>/", views.district_news, name="district_news"),

    # 3. News Detail (SEO Friendly)
    path("<str:url_city>/<slug:slug>.html", views.news_detail, name="news_detail"),
    path("news/<slug:slug>.html", views.news_detail, name="news_detail_simple"),

    # 4. Utilities & SEO
    path("fix-img/", views.fix_webp_image, name="fix_webp_image"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("ads.txt", views.ads_txt, name="ads_txt"),

    # 5. Static Pages
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
]
