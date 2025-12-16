from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("national/", views.national_news, name="national_news"),

    # SEO + Secure URL
    path(
        "news/<slug:slug>-<str:code>/",
        views.news_detail,
        name="news_detail"
    ),

    path("district/<str:district>/", views.district_news, name="district_news"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    # ads.txt at root
    path("ads.txt", views.ads_txt, name="ads_txt"),
]
