from django.urls import path
from . import views
from .views import robots_txt, sitemap_xml

urlpatterns = [
    # ===== CORE PAGES =====
    path("", views.home, name="home"),
    path("national/", views.national_news, name="national_news"),
    path("international/", views.international_news, name="international_news"),
    path("district/<str:district>/", views.district_news, name="district_news"),

    # ===== SEO / SYSTEM FILES =====
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
    path("ads.txt", views.ads_txt, name="ads_txt"),
    # ===== adseence important page=====
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),

    # ===== NEWS DETAIL (ALWAYS LAST) =====
    path("<slug:slug>/", views.news_detail, name="news_detail"),
]
