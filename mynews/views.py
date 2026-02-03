import re, requests, os, logging, html
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"
SITE_NAME = "Uttar World News"

def get_common_sidebar_data():
    return {
        "bazaar_sidebar": News.objects.filter(category="Market").order_by("-date")[:5],
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
    }

# --- 1. HOME PAGE LOGIC (3 Badi News + Baki Cards) ---
def home(request):
    try:
        query = request.GET.get("q")
        if query:
            news_list = News.objects.filter(title__icontains=query).order_by("-date")
            page_obj = Paginator(news_list, 60).get_page(request.GET.get("page"))
            return render(request, "mynews/home.html", {"page_obj": page_obj, **get_common_sidebar_data()})
        
        # News nikalna
        all_important = News.objects.filter(is_important=True).order_by("-date")
        
        # A. Top 3 Highlights (With 50 Words Content)
        top_3_highlights = all_important[:3]
        for n in top_3_highlights:
            clean = strip_tags(n.content)
            # AdSense Fix: 50 words approx 300 characters
            n.clean_home_text = html.unescape(clean).replace('\xa0', ' ').strip()[:300] + "..."

        # B. Other News (Sirf Card: Title, Image, Date, Day)
        other_news = all_important[3:43] # Agli 40 news cards ke liye

        context = {
            "top_3_highlights": top_3_highlights,
            "other_news": other_news,
            "meta_description": "Uttar World News: Latest breaking news from UP, India.",
            "meta_keywords": "Uttar World, UttarWorld News, Latest UP News",
        }
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)

    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse("Home Page Error", status=500)

# --- 2. NEWS DETAIL ---
def news_detail(request, url_city, slug): 
    news = get_object_or_404(News, slug=slug, url_city=url_city)
    related_news = News.objects.filter(category=news.category).exclude(id=news.id).order_by("-date")[:3]
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", news.youtube_url)
        v_id = match.group(1) if match else None
    context = {"news": news, "related_news": related_news, "v_id": v_id}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/news_detail.html", context)

# --- 3. ALL CATEGORY VIEWS (SARE PAGES) ---
def national_news(request):
    news_list = News.objects.filter(category="National").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    return render(request, "mynews/home.html", {"page_obj": page_obj, "category": "National", **get_common_sidebar_data()})

def international_news(request):
    news_list = News.objects.filter(category="International").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    return render(request, "mynews/home.html", {"page_obj": page_obj, "category": "International", **get_common_sidebar_data()})

def technology(request):
    news_list = News.objects.filter(category="Technology").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    return render(request, "mynews/home.html", {"page_obj": page_obj, "category": "Technology", **get_common_sidebar_data()})

def bollywood(request):
    news_list = News.objects.filter(category="Bollywood").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    return render(request, "mynews/home.html", {"page_obj": page_obj, "category": "Bollywood", **get_common_sidebar_data()})

def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    return render(request, "mynews/home.html", {"district": district, "page_obj": page_obj, **get_common_sidebar_data()})

# --- 4. STATIC & SITEMAP ---
def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        city = n.url_city or "news"
        xml += f'  <url><loc>{SITE_URL}/{city}/{n.slug}.html</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request): return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml", content_type="text/plain")
def ads_txt(request): return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
def privacy_policy(request): return render(request, "mynews/privacy_policy.html")
def about_us(request): return render(request, "mynews/about_us.html")
def contact_us(request): return render(request, "mynews/contact_us.html")
def disclaimer(request): return render(request, "mynews/disclaimer.html")
