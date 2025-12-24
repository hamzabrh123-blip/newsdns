import random
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.core.cache import cache
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse

from .models import News, Comment, AdminOTP

ADMIN_EMAIL = "hamzabrh@gmail.com"

# ================= ADMIN LOGIN =================
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if email != ADMIN_EMAIL:
            messages.error(request, "You are not authorized!")
            return redirect("admin_login")

        otp = str(random.randint(100000, 999999))
        AdminOTP.objects.create(email=email, otp=otp)

        send_mail(
            "Admin Login OTP",
            f"Your OTP is: {otp}",
            ADMIN_EMAIL,
            [email],
            fail_silently=False,
        )

        request.session["admin_email"] = email
        return redirect("admin_verify")

    return render(request, "admin_login.html")


def admin_verify(request):
    if request.method == "POST":
        entered = request.POST.get("otp")
        email = request.session.get("admin_email")

        data = AdminOTP.objects.filter(email=email).last()

        if data and data.otp == entered:
            user, _ = User.objects.get_or_create(
                username="otpadmin",
                defaults={
                    "email": email,
                    "is_staff": True,
                    "is_superuser": True,
                }
            )
            login(request, user)
            return redirect("/admin/")

        messages.error(request, "Invalid OTP!")

    return render(request, "admin_verify.html")


# ================= HOME =================
def home(request):
    query = request.GET.get("q")

    if query:
        news_list = News.objects.filter(title__icontains=query).order_by("-date")
    else:
        news_list = News.objects.filter(
            models.Q(category__iexact="International") |
            models.Q(is_important=True)
        ).order_by("-date")

    paginator = Paginator(news_list, 12)  # 12 news per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    important = News.objects.filter(is_important=True).order_by("-date")[:5]

    visits = cache.get("visits", 0) + 1
    cache.set("visits", visits, None)

    return render(request, "mynews/home.html", {
        "page_obj": page_obj,
        "important": important,
        "visits": visits
    })


# ================= NATIONAL =================
def national_news(request):
    news_list = News.objects.filter(category="National").order_by("-date")
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "mynews/national_news.html", {
        "page_obj": page_obj
    })


# ================= NEWS DETAIL =================
def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)

    # Sidebar latest news
    sidebar_news = News.objects.exclude(id=news.id).order_by("-id")[:10]

    # Comments
    comments = Comment.objects.filter(news=news).order_by("-date")

    # YouTube embed fix
    if news.youtube_url:
        if "watch?v=" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace("watch?v=", "embed/")
        elif "youtu.be/" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace("youtu.be/", "www.youtube.com/embed/")

    return render(request, "mynews/news_detail.html", {
        "news": news,
        "sidebar_news": sidebar_news,
        "comments": comments
    })


# ================= DISTRICT =================
def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "mynews/district_news.html", {
        "district": district,
        "page_obj": page_obj
    })


# ================= STATIC PAGES =================
def about(request):
    return render(request, "mynews/about.html")


def contact(request):
    return render(request, "mynews/contact.html")


# ================= CREATE ADMIN =================
def create_admin(request):
    User = get_user_model()

    if User.objects.filter(username="hamzareal").exists():
        return HttpResponse("Admin already exists")

    User.objects.create_superuser(
        username="hamzareal",
        email="hamzareal@gmail.com",
        password="Hamza@5555"
    )
    return HttpResponse("Admin Created Successfully!")


# ================= ADS.TXT =================
def ads_txt(request):
    return HttpResponse(
        "google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0",
        content_type="text/plain"
    )


# ================= ADD NEWS =================
def add_news(request):
    if request.method == "POST":
        News.objects.create(
            title=request.POST["title"],
            slug=request.POST["slug"],
            content=request.POST["content"]
        )
        return redirect("home")

    return render(request, "mynews/add_news.html")
