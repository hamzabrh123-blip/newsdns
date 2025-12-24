from .views import robots_txt
from django.urls import path, re_path
from django.shortcuts import redirect
from . import views

def news_redirect(request, slug, code):
    return redirect("news_detail", slug=slug, permanent=True)

urlpatterns = [
    path("robots.txt", robots_txt),
    path("", views.home, name="home"),
    path("national/", views.national_news, name="national_news"),

    # ✅ NEW clean SEO URL
    path("<slug:slug>", views.news_detail, name="news_detail"),

    # 🔁 OLD URL → 301 redirect
    re_path(r'^(?P<slug>[-\w\d\u0900-\u097F]+)$', views.news_detail, name='news_detail'),

    path("add-news/", views.add_news, name="add_news"),
    path("district/<str:district>/", views.district_news, name="district_news"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("ads.txt", views.ads_txt, name="ads_txt"),
]
