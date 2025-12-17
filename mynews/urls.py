from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    re_path(r'^news/(?P<slug>[-\w\d\u0900-\u097F]+)/(?P<code>[^/]+)/$', views.news_detail, name='news_detail'),
    path("national/", views.national_news, name="national_news"),

    # SEO + Secure URL
    path(
        "news/<slug:slug>-<str:code>/",
        views.news_detail,
        name="news_detail"
    ),

    # ✅ Add news page
    path("add-news/", views.add_news, name="add_news"),

    # ✅ SEO Friendly News URL (ID hata diya)
    re_path(r'^news/(?P<slug>[-\w\d\u0900-\u097F]+)/$', views.news_detail, name='news_detail'),
    path("district/<str:district>/", views.district_news, name="district_news"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    # ads.txt at root
    path("ads.txt", views.ads_txt, name="ads_txt"),
]
