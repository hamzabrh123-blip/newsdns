import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

from .models import News
from .constants import LOCATION_DATA

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"

# --- API FOR BULK PC SCRIPT ---
def fb_news_api(request):
    news_list = News.objects.filter(status='Published').order_by('-date')[:20]
    data = []
    for n in news_list:
        city = n.url_city if n.url_city else 'news'
        data.append({
            'id': n.id,
            'title': n.title,
            'url': f"{SITE_URL.rstrip('/')}/{city}/{n.slug}/"
        })
    return JsonResponse(data, safe=False)

# --- Common Sidebar Data (Fixed Filters) ---
def get_common_sidebar_data():
    published = News.objects.filter(status='Published')
    used_districts = published.values_list('district', flat=True).distinct()
    dynamic_cities = []

    # In keys को साइडबार के सिटी लिस्ट से दूर रखना है
    exclude_keys = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi', 'Other-States']

    for eng, hin, cat_slug in LOCATION_DATA:
        if eng in used_districts and eng not in exclude_keys:
            dynamic_cities.append({'id': eng, 'name': hin})

    return {
        "up_sidebar": published.order_by("-date")[:10],
        "bharat_sidebar": published.filter(district__iexact="National")[:5],
        "world_sidebar": published.filter(district__iexact="International")[:5],
        "bazaar_sidebar": published.filter(district__iexact="Market")[:5],
        "sports_sidebar": published.filter(district__iexact="Sports")[:5],
        "dynamic_up_cities": dynamic_cities,
    }

# --- 1. HOME PAGE (STRICT CATEGORY FIX) ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status='Published').order_by("-date")
        
        # 1. World & National (Strict iexact matching - No more icontains mess)
        world_news = all_news.filter(district__iexact="International")[:4]
        national_news = all_news.filter(district__iexact="National")[:4]

        # 2. UP NEWS SECTION (Exclude Non-UP Districts)
        non_up_labels = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market']
        
        # UP News wahi hain jo upar ki labels mein nahi aati aur jinka district null nahi hai
        up_news_qs = all_news.exclude(district__in=non_up_labels).exclude(district__isnull=True)

        context = {
            "top_5_highlights": all_news.filter(show_in_highlights=True)[:5],
            "up_news": up_news_qs[:12], 
            "national_news": national_news,
            "world_news": world_news,
            "bollywood_news": all_news.filter(district__iexact="Bollywood")[:4],
            "sports_news": all_news.filter(district__iexact="Sports")[:4],
            "other_news": Paginator(all_news, 10).get_page(request.GET.get('page')),
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse(f"Server Error: {e}")

# --- DETAIL & DISTRICT VIEWS ---
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug=slug)
    v_id = None
    if news.youtube_url:
        regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
        match = re.search(regex, news.youtube_url)
        if match: v_id = match.group(1)
    
    context = {
        "news": news,
        "og_title": news.title,
        "related_news": News.objects.filter(district=news.district, status='Published').exclude(id=news.id).order_by("-date")[:6],
        "v_id": v_id,
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

def district_news(request, district):
    # Search in district field strictly first
    news_list = News.objects.filter(status='Published').filter(
        Q(district__iexact=district) | Q(url_city__iexact=district)
    ).order_by("-date")
    
    return render(request, "mynews/district_news.html", {
        "district": district, 
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get('page')), 
        **get_common_sidebar_data()
    })

# --- UTILS (Sitemap, Robots, etc.) ---
def sitemap_xml(request):
    items = News.objects.filter(status='Published').order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        xml += f'<url><loc>{SITE_URL.rstrip("/")}/{n.url_city or "news"}/{n.slug}/</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    return HttpResponse(xml + '</urlset>', content_type="application/xml")

def robots_txt(request): return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")
def ads_txt(request): return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
