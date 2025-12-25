from django.urls import path
from . import views
from .views import robots_txt, sitemap_xml

urlpatterns = [
    # ===== CORE PAGES =====
    path("", views.home, name="home"),
    path("national/", views.national_news, name="national_news"),
    path("district/<str:district>/", views.district_news, name="district_news"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    # ===== SEO / SYSTEM FILES =====
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
    path("ads.txt", views.ads_txt, name="ads_txt"),

    # ===== NEWS DETAIL (ALWAYS LAST) =====
    path("<path:slug>/", views.news_detail, name="news_detail"),
]
