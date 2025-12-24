from django.urls import path, re_path
from django.shortcuts import redirect
from . import views
from .views import robots_txt, sitemap_xml   # ✅ IMPORTANT IMPORT

def news_redirect(request, slug, code):
    return redirect("news_detail", slug=slug, permanent=True)

urlpatterns = [
    # ===== CORE PAGES =====
    path("", views.home, name="home"),
    path("national/", views.national_news, name="national_news"),
    path("district/<str:district>/", views.district_news, name="district_news"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("add-news/", views.add_news, name="add_news"),

    # ===== SEO / SYSTEM FILES (ALWAYS ABOVE SLUG) =====
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
    path("ads.txt", views.ads_txt, name="ads_txt"),

    # ===== NEWS DETAIL (LAST) =====
    path("<slug:slug>/", views.news_detail, name="news_detail"),
]
