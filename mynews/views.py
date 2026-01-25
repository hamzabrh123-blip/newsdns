from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News, Comment
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_common_sidebar_data():
    return {
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:10],
        "technology_sidebar": News.objects.filter(category="Technology").order_by("-date")[:3],
        "bollywood_sidebar": News.objects.filter(category="Bollywood").order_by("-date")[:3],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
        "up_national_sidebar": News.objects.filter(district='UP-National').order_by("-date")[:3],
        "purvanchal_sidebar": News.objects.filter(district='Purvanchal').order_by("-date")[:5],
        "bahraich_gonda_sidebar": News.objects.filter(district='Bahraich-Gonda').order_by("-date")[:10],
        "balrampur_shravasti_sidebar": News.objects.filter(district='Balrampur-Shravasti').order_by("-date")[:3],
        "sitapur_barabanki_sidebar": News.objects.filter(district='Sitapur-Barabanki').order_by("-date")[:5],
    }

def home(request):
    query = request.GET.get("q")
    news_list = News.objects.filter(title__icontains=query).order_by("-date") if query else News.objects.filter(is_important=True).order_by("-date")
    paginator = Paginator(news_list, 20) 
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "meta_description": "UP Halchal News: Latest Uttar Pradesh News in Hindi.",
        "og_title": "UP Halchal News",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/home.html", context)

# ✅ FIXED & IMPROVED: Related News logic added
def news_detail(request, url_city, slug): 
    # न्यूज़ को slug और url_city के आधार पर ढूँढना
    news = get_object_or_404(News, slug=slug, url_city=url_city)
    
    # सम्बन्धित खबरें: उसी शहर (district) की 3 ताजा खबरें (वर्तमान न्यूज़ को छोड़कर)
    related_news = News.objects.filter(district=news.district).exclude(id=news.id).order_by("-date")[:3]
    
    comments = Comment.objects.filter(news=news, active=True).order_by("-date")
    
    # Youtube URL logic (Template handles this, but keeping for safety)
    if news.youtube_url:
        if "watch?v=" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace("watch?v=", "embed/")
        elif "youtu.be/" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace("youtu.be/", "www.youtube.com/embed/")
    
    context = {
        "news": news, 
        "comments": comments,
        "related_news": related_news  # ✅ अब टेम्पलेट में खबरें दिखेंगी
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/news_detail.html", context)

# Redirect old news to new URL format
def old_news_redirect(request, slug):
    news = get_object_or_404(News, slug=slug)
    city = news.url_city if news.url_city else "news"
    return redirect(f'/{city}/{news.slug}.html', permanent=True)

# अन्य views जैसे हैं वैसे ही रहेंगे...
def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"district": district, "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

# ... (बाकी के views National, Technology, Bollywood, International सब सही हैं)

def contact_us(request):
    success = False
    if request.method == "POST":
        try:
            send_mail(f"Message from {request.POST.get('name')}", request.POST.get('message'), settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            success = True
        except: pass
    context = {"success": success}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/contact_us.html", context)

# Static Pages
def privacy_policy(request): return render(request, "mynews/privacy_policy.html")
def about_us(request): return render(request, "mynews/about_us.html")
def disclaimer(request): return render(request, "mynews/disclaimer.html")
def ads_txt(request): return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
def robots_txt(request): return HttpResponse("User-Agent: *\nAllow: /\nSitemap: https://halchal.onrender.com/sitemap.xml", content_type="text/plain")

def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += "<url><loc>https://halchal.onrender.com/</loc></url>"
    for n in items:
        xml += f"<url><loc>https://halchal.onrender.com/{n.url_city or 'news'}/{n.slug}.html</loc></url>"
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")
