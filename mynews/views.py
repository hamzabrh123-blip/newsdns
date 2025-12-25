from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.db import models
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News, Comment
from django.conf import settings


# ================= HOME =================
def home(request):
    query = request.GET.get("q")
    try:
        if query:
            news_list = News.objects.filter(title__icontains=query).order_by("-date")
        else:
            news_list = News.objects.filter(
                models.Q(category__iexact="International") |
                models.Q(is_important=True)
            ).order_by("-date")
    except Exception:
        news_list = News.objects.none()

    paginator = Paginator(news_list, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    try:
        important = News.objects.filter(is_important=True).order_by("-date")[:5]
    except Exception:
        important = []

    return render(request, "mynews/home.html", {"page_obj": page_obj, "important": important})


# ================= NATIONAL =================
def national_news(request):
    news_list = News.objects.filter(category="National").order_by("-date")
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "mynews/national_news.html", {"page_obj": page_obj})


# ================= NEWS DETAIL =================
def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    sidebar_news = News.objects.exclude(id=news.id).order_by("-id")[:10]
    comments = Comment.objects.filter(news=news).order_by("-date")

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
    return render(request, "mynews/district_news.html", {"district": district, "page_obj": page_obj})


# ================= STATIC PAGES =================
def privacy_policy(request):
    return render(request, "mynews/privacy_policy.html")

def about_us(request):
    return render(request, "mynews/about_us.html")
    
def disclaimer(request):
    return render(request, "mynews/disclaimer.html")

def contact_us(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
    # Send email to admin
        send_mail(
            subject=f"Contact Form: {name}",
            message=f"From: {name} <{email}>\n\n{message}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
        )

        return render(request, "mynews/contact_us.html", {"success": True})

    return render(request, "mynews/contact_us.html")

# ================= ADS.TXT =================
def ads_txt(request):
    return HttpResponse(
        "google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0",
        content_type="text/plain"
    )


# ================= ROBOTS.TXT =================
def robots_txt(request):
    return HttpResponse(
        "User-Agent: *\n"
        "Disallow:\n\n"
        "Sitemap: https://halchal.up.railway.app/sitemap.xml",
        content_type="text/plain"
    )


# ================= SITEMAP.XML =================
def sitemap_xml(request):
    base_url = "https://halchal.up.railway.app"
    urls = [f"{base_url}/"]

    for news in News.objects.exclude(slug__isnull=True).exclude(slug=""):
        urls.append(f"{base_url}/{news.slug}")

    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for url in urls:
        xml += f"<url><loc>{url}</loc></url>"
    xml += "</urlset>"

    return HttpResponse(xml, content_type="application/xml")
