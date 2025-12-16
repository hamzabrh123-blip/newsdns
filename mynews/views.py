import base64
import random

from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.core.cache import cache
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse

from .models import News, Comment, AdminOTP


ADMIN_EMAIL = "hamzabrh@gmail.com"


# 🔐 Decode encoded news id
def decode_id(code):
    try:
        padded = code + "=" * (-len(code) % 4)
        decoded = base64.urlsafe_b64decode(padded).decode()
        prefix, news_id = decoded.split(":")
        if prefix != "news":
            raise ValueError
        return int(news_id)
    except Exception:
        raise Http404("Invalid news")


# 🔑 Admin Login – Send OTP
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


# ✅ Verify OTP
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
                },
            )
            login(request, user)
            return redirect("/admin/")

        messages.error(request, "Invalid OTP!")

    return render(request, "admin_verify.html")


# 🏠 Home Page
def home(request):
    query = request.GET.get("q")

    if query:
        news_list = News.objects.filter(title__icontains=query)
    else:
        news_list = News.objects.filter(
            models.Q(category__iexact="International")
            | models.Q(is_important=True)
        ).order_by("-date")[:12]

    important = News.objects.filter(is_important=True)[:5]

    visits = cache.get("visits", 0) + 1
    cache.set("visits", visits, None)

    return render(
        request,
        "mynews/home.html",
        {
            "news_list": news_list,
            "important": important,
            "visits": visits,
        },
    )


# 🇮🇳 National News
def national_news(request):
    news_list = News.objects.filter(category="National").order_by("-date")
    return render(request, "mynews/national_news.html", {"news_list": news_list})


# 📰 News Detail Page
def news_detail(request, slug, code):
    news_id = decode_id(code)
    news = get_object_or_404(News, id=news_id)
    comments = Comment.objects.filter(news=news).order_by("-date")

    return render(
        request,
        "mynews/news_detail.html",
        {
            "news": news,
            "comments": comments,
        },
    )


# 🗺️ District-wise News
def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    return render(
        request,
        "mynews/district_news.html",
        {
            "district": district,
            "news_list": news_list,
        },
    )


# 📄 Static Pages
def about(request):
    return render(request, "mynews/about.html")


def contact(request):
    return render(request, "mynews/contact.html")


# 🔐 Create Super Admin (one-time)
def create_admin(request):
    UserModel = get_user_model()

    if UserModel.objects.filter(username="hamzareal").exists():
        return HttpResponse("Admin already exists")

    UserModel.objects.create_superuser(
        username="hamzareal",
        email="hamzareal@gmail.com",
        password="Hamza@5555",
    )

    return HttpResponse("Admin Created Successfully!")


# 📊 Visit Counter (Sidebar)
def visit_counter(request):
    visits = cache.get("visits", 0) + 1
    cache.set("visits", visits, None)
    return render(request, "sidebar.html", {"visits": visits})


# 📢 ads.txt
def ads_txt(request):
    content = "google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")
