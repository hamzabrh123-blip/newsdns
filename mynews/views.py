import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from .models import News
from django.utils.html import strip_tags
from django.db.models import Q

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

# --- Common Data Function ---
def get_common_sidebar_data():
    used_districts = News.objects.filter(status='Published').values_list('district', flat=True).distinct()
    dynamic_cities = []
    exclude_from_up = [
        'National', 'International', 'Sports', 'Bollywood', 
        'Hollywood', 'Technology', 'Market', 'Delhi', 'Other-States'
    ]
    for eng, hin, cat_slug in News.LOCATION_DATA:
        if eng in used_districts and eng not in exclude_from_up:
            dynamic_cities.append({'id': eng, 'name': hin})
    
    return {
        "up_sidebar": News.objects.filter(status='Published').order_by("-date")[:10],
        "bharat_sidebar": News.objects.filter(category="National", status='Published').order_by("-date")[:5],
        "world_sidebar": News.objects.filter(category="International", status='Published').order_by("-date")[:5],
        "bazaar_sidebar": News.objects.filter(category="Market", status='Published').order_by("-date")[:5],
        "sports_sidebar": News.objects.filter(category="Sports", status='Published').order_by("-date")[:5],
        "dynamic_up_cities": dynamic_cities,
    }

# --- 1. HOME PAGE ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        query = request.GET.get("q")
        published_news = News.objects.filter(status='Published').order_by("-date")

        if query:
            news_list = published_news.filter(title__icontains=query)
            page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
            return render(request, "mynews/home.html", {"page_obj": page_obj, **common_data})
        
        top_highlights = News.objects.filter(show_in_highlights=True, status='Published').order_by("-date")[:5]
        
        context = {
            "top_5_highlights": top_highlights,
            "up_news": published_news[:4],
            "national_news": published_news.filter(category="National")[:4],
            "world_news": published_news.filter(category="International")[:4],
            "sports_news": published_news.filter(category="Sports")[:4],
            "bollywood_news": published_news.filter(Q(district="Bollywood") | Q(category="Bollywood"))[:4],
            "technology_news": published_news.filter(Q(district="Technology") | Q(category="Technology"))[:4],
            "other_news": Paginator(published_news, 10).get_page(request.GET.get('page')),
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse("System Update in Progress...", status=200)

# --- 2. NEWS DETAIL ---
def news_detail(request, url_city, slug): 
    news = get_object_or_404(News, slug=slug)
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", news.youtube_url)
        v_id = match.group(1) if match else None
        
    context = {
        "news": news, 
        "og_title": news.title,
        "related_news": News.objects.filter(category=news.category, status='Published').exclude(id=news.id).order_by("-date")[:6],
        "v_id": v_id,
        "meta_description": strip_tags(news.content)[:160] if news.content else news.title,
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT/CATEGORY VIEW ---
def district_news(request, district):
    news_list = News.objects.filter(status='Published').filter(
        Q(district__iexact=district) | 
        Q(category__icontains=district) | 
        Q(url_city__iexact=district)
    ).order_by("-date")
    
    page_obj = Paginator(news_list, 15).get_page(request.GET.get('page'))
    return render(request, "mynews/district_news.html", {
        "district": district, 
        "page_obj": page_obj, 
        "news_count": news_list.count(),
        **get_common_sidebar_data()
    })

# --- 4. SEO & LEGAL ---
def sitemap_xml(request):
    items = News.objects.filter(status='Published').order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        city = n.url_city if n.url_city else 'news'
        xml += f'  <url><loc>{SITE_URL.rstrip("/")}/{city}/{n.slug}/</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request): return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")
def ads_txt(request): return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
