from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.db import models
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News, Comment
from django.conf import settings
import logging

# Logger setup
logger = logging.getLogger(__name__)

# ✅ OPTIMIZED SIDEBAR DATA
def get_common_sidebar_data():
    return {
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:3],
        "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:3],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
        "purvanchal_sidebar": News.objects.filter(district='Purvanchal').order_by("-date")[:10],
        "bahraich_gonda_sidebar": News.objects.filter(district='Bahraich-Gonda').order_by("-date")[:10],
        "sitapur_barabanki_sidebar": News.objects.filter(district='Sitapur-Barabanki').order_by("-date")[:5],
    }

# ================= HOME (MODIFIED) =================
def home(request):
    query = request.GET.get("q")
    if query:
        news_list = News.objects.filter(title__icontains=query).order_by("-date")
    else:
        news_list = News.objects.filter(is_important=True).order_by("-date")

    paginator = Paginator(news_list, 20) 
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {"page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/home.html", context)

# ================= NATIONAL NEWS =================
def national_news(request):
    news_list = News.objects.filter(category="National").order_by("-date")
    paginator = Paginator(news_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "district": "भारत (National)",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

# ================= INTERNATIONAL NEWS =================
def international_news(request):
    news_list = News.objects.filter(category="International").order_by("-date")
    paginator = Paginator(news_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "district": "दुनिया (International)",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

# ================= NEWS DETAIL =================
def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    comments = Comment.objects.filter(news=news).order_by("-date")

    if news.youtube_url:
        if "watch?v=" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace("watch?v=", "embed/")
        elif "youtu.be/" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace("youtu.be/", "www.youtube.com/embed/")

    context = {
        "news": news,
        "comments": comments,
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/news_detail.html", context)

# ================= DISTRICT =================
def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    paginator = Paginator(news_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "district": district, 
        "page_obj": page_obj
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

# ================= CONTACT US =================
def contact_us(request):
    success = False
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message_body = request.POST.get("message")
        
        subject = f"UP Halchal News: Message from {name}"
        full_message = f"Sender Name: {name}\nSender Email: {email}\n\nMessage:\n{message_body}"
        
        try:
            send_mail(
                subject=subject,
                message=full_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            success = True
        except Exception as e:
            print(f"Email Error: {e}") 
            logger.error(f"Contact Form Error: {e}")
            success = True 

    context = {"success": success}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/contact_us.html", context)

# ================= STATIC PAGES =================
def privacy_policy(request):
    return render(request, "mynews/privacy_policy.html")

def about_us(request):
    return render(request, "mynews/about_us.html")
    
def disclaimer(request):
    return render(request, "mynews/disclaimer.html")

# ================= SEO & ADS =================
# 1. Google AdSense ke liye ads.txt
def ads_txt(request):
    content = "google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")

# 2. Search Engines ke liye robots.txt
def robots_txt(request):
    content = (
        "User-Agent: *\n"
        "Allow: /\n"
        "Disallow: /admin_login.html\n"
        "Disallow: /admin_verify.html\n"
        "Sitemap: https://halchal.onrender.com/sitemap.xml"
    )
    return HttpResponse(content, content_type="text/plain")

# 3. Google Indexing ke liye sitemap.xml
def sitemap_xml(request):
    # Railway hata kar yahan Render wala URL hi rakhein
    base_url = "https://halchal.onrender.com" 
    news_items = News.objects.exclude(slug__isnull=True).exclude(slug="").order_by('-date')[:500]
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    
    # 1. Homepage
    xml += f"<url><loc>{base_url}/</loc><priority>1.0</priority></url>"
    
    # 2. News Pages
    for news in news_items:
        # ✅ Slug ke aage '/' lagana bahut zaroori hai
        url = f"{base_url}/{news.slug}/" 
        xml += f"<url><loc>{url}</loc><priority>0.8</priority></url>"
        
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")
