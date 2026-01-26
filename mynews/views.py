from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News, Comment
from django.conf import settings
from django.utils.html import strip_tags
import logging

# Professional Website Configuration
SITE_URL = "https://uttarworld.com"
SITE_NAME = "Uttar World News"

def get_common_sidebar_data():
    return {
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:10],
        "technology_sidebar": News.objects.filter(category="Technology").order_by("-date")[:3],
        "bollywood_sidebar": News.objects.filter(category="Bollywood").order_by("-date")[:3],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
    }

def home(request):
    query = request.GET.get("q")
    news_list = News.objects.filter(title__icontains=query).order_by("-date") if query else News.objects.filter(is_important=True).order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    
    context = {
        "page_obj": page_obj,
        "meta_description": "Uttar World News: Get the latest breaking news from Uttar Pradesh, India, and around the world.",
        "meta_keywords": "Uttar World, UttarWorld News, Latest UP News, Breaking News India",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/home.html", context)

def national_news(request):
    news_list = News.objects.filter(category="National").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"category": "National", "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/category_news.html", context)

def international_news(request):
    news_list = News.objects.filter(category="International").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"category": "International", "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/category_news.html", context)

def technology(request):
    news_list = News.objects.filter(category="Technology").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"category": "Technology", "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/category_news.html", context)

def bollywood(request):
    news_list = News.objects.filter(category="Bollywood").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"category": "Bollywood", "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/category_news.html", context)

def news_detail(request, url_city, slug): 
    # Yahan dhyan dein: slug aur url_city dono match hone chahiye
    news = get_object_or_404(News, slug=slug, url_city=url_city)
    related_news = News.objects.filter(district=news.district).exclude(id=news.id).order_by("-date")[:3]
    
    clean_text = strip_tags(news.content)
    english_description = f"Read full details about {news.title} at Uttar World News."
    
    context = {
        "news": news, 
        "related_news": related_news,
        "meta_description": english_description,
        "og_title": f"{news.title} | {SITE_NAME}",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/news_detail.html", context)

def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"district": district, "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

def contact_us(request):
    success = False
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        full_msg = f"Inquiry from: {name}\nEmail: {email}\n\nMessage:\n{message}"
        try:
            send_mail(f"New Contact from {name}", full_msg, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            success = True
        except: pass
    
    context = {"success": success}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/contact_us.html", context)

def privacy_policy(request): return render(request, "mynews/privacy_policy.html")
def about_us(request): return render(request, "mynews/about_us.html")
def disclaimer(request): return render(request, "mynews/disclaimer.html")

def ads_txt(request): 
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def robots_txt(request):
    content = f"User-Agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {SITE_URL}/sitemap.xml"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:1000]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += f"  <url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>\n"
    for n in items:
        # Agar url_city nahi hai toh 'news' default rakhte hain taaki link na toote
        city = n.url_city if n.url_city else "news"
        xml += f"  <url>\n    <loc>{SITE_URL}/{city}/{n.slug}.html</loc>\n    <lastmod>{n.date.strftime('%Y-%m-%d')}</lastmod>\n    <priority>0.8</priority>\n  </url>\n"
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")
