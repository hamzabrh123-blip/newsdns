import re
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News
from django.conf import settings
from django.utils.html import strip_tags

# Professional Website Configuration
SITE_URL = "https://uttarworld.com"
SITE_NAME = "Uttar World News"

# --- Naya Function Video ID nikalne ke liye ---
def extract_video_id(url):
    if not url:
        return None
    # Ye regex har tarah ke YouTube link (short, long, watch, embed) se ID nikal lega
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_common_sidebar_data():
    return {
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:10],
        "technology_sidebar": News.objects.filter(category="Technology").order_by("-date")[:3],
        "bollywood_sidebar": News.objects.filter(category="Bollywood").order_by("-date")[:3],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
    }

def home(request):
    try:
        query = request.GET.get("q")
        news_list = News.objects.filter(title__icontains=query).order_by("-date") if query else News.objects.filter(is_important=True).order_by("-date")
        page_obj = Paginator(news_list, 60).get_page(request.GET.get("page"))
        
        context = {
            "page_obj": page_obj,
            "meta_description": "Uttar World News: Get the latest breaking news from Uttar Pradesh, India, and around the world.",
            "meta_keywords": "Uttar World, UttarWorld News, Latest UP News, Breaking News India",
        }
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except:
        return HttpResponse("Home Page Loading Error", status=500)

def national_news(request):
    try:
        news_list = News.objects.filter(category="National").order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"category": "National", "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except:
        return redirect('home')

def international_news(request):
    try:
        news_list = News.objects.filter(category="International").order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"category": "International", "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except:
        return redirect('home')

def technology(request):
    try:
        news_list = News.objects.filter(category="Technology").order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"category": "Technology", "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except:
        return redirect('home')

def bollywood(request):
    try:
        news_list = News.objects.filter(category="Bollywood").order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"category": "Bollywood", "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except:
        return redirect('home')

# --- YAHAN DEKHO: news_detail updated ---
def news_detail(request, url_city, slug): 
    try:
        news = get_object_or_404(News, slug=slug, url_city=url_city)
        related_news = News.objects.filter(district=news.district).exclude(id=news.id).order_by("-date")[:3]
        
        # Video ID yahan nikal kar bhej rahe hain
        v_id = extract_video_id(news.youtube_url)
        
        context = {
            "news": news, 
            "related_news": related_news,
            "meta_description": strip_tags(news.content)[:160],
            "og_title": f"{news.title} | {SITE_NAME}",
            "v_id": v_id,  # Ab ye HTML mein use hoga
        }
        context.update(get_common_sidebar_data())
        return render(request, "mynews/news_detail.html", context)
    except:
        return redirect('home')

def district_news(request, district):
    try:
        news_list = News.objects.filter(district__iexact=district).order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"district": district, "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except:
        return redirect('home')

def contact_us(request):
    success = False
    if request.method == "POST":
        try:
            send_mail(f"Contact", request.POST.get('message'), settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
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
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += f"  <url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>\n"
    for n in items:
        city = n.url_city if n.url_city else "news"
        xml += f"  <url>\n    <loc>{SITE_URL}/{city}/{n.slug}.html</loc>\n    <lastmod>{n.date.strftime('%Y-%m-%d')}</lastmod>\n  </url>\n"
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")
