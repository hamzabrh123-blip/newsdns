import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.utils.html import strip_tags
from django.db.models import Q

from .models import News
from .constants import LOCATION_DATA

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"

# --- HELPER: Sidebar Data (Isse performance badhegi) ---
def get_common_sidebar_data():
    published = News.objects.filter(status='Published')
    
    # Districts sidebar list filter
    exclude_keys = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Entertainment']
    used_districts = published.values_list('district', flat=True).distinct()
    
    dynamic_cities = []
    for eng, hin, cat_slug in LOCATION_DATA:
        if eng in used_districts and eng not in exclude_keys:
            dynamic_cities.append({'id': eng, 'name': hin})

    return {
        "up_sidebar": published.order_by("-date")[:10],
        "bharat_sidebar": published.filter(Q(category="National") | Q(district="National"))[:5],
        "world_sidebar": published.filter(Q(category="International") | Q(district="International"))[:5],
        "bazaar_sidebar": published.filter(Q(category="Market") | Q(district="Market"))[:5],
        "sports_sidebar": published.filter(Q(category="Sports") | Q(district="Sports"))[:5],
        "dynamic_up_cities": dynamic_cities,
    }

# --- 1. HOME PAGE ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status='Published').order_by("-date")
        
        # Page number handle
        try:
            page_number = int(request.GET.get('page', 1))
        except ValueError:
            page_number = 1
            
        paginator = Paginator(all_news, 12) 
        other_news_page = paginator.get_page(page_number)
        
        exclude_cats = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market']
        
        context = {
            "other_news": other_news_page, 
            "page_number": page_number,
            **common_data
        }

        # Page 1 par extra sections dikhao
        if page_number == 1:
            context.update({
                "top_5_highlights": all_news.filter(show_in_highlights=True)[:5],
                "national_news": all_news.filter(category="National")[:4],
                "world_news": all_news.filter(category="International")[:4],
                "up_news": all_news.exclude(category__in=exclude_cats)[:12],
                "entertainment_news": all_news.filter(category__in=['Bollywood', 'Hollywood'])[:6],
                "bazaar_news": all_news.filter(category="Market")[:4],
            })

        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse("Server Updating... Please refresh in a minute.")

# --- 2. NEWS DETAIL ---
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug=slug, status='Published')
    
    # UPGRADED YouTube ID Extractor
    v_id = None
    if news.youtube_url:
        regex = r"(?:v=|youtu\.be/|shorts/|embed/|live/|^)([a-zA-Z0-9_-]{11})(?:\?|&|$| )"
        match = re.search(regex, news.youtube_url)
        if match: 
            v_id = match.group(1)

    context = {
        "news": news,
        "v_id": v_id,
        "related_news": News.objects.filter(category=news.category, status='Published').exclude(id=news.id).order_by("-date")[:6],
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT / CATEGORY ---
def district_news(request, district):
    news_list = News.objects.filter(status='Published').filter(
        Q(district__iexact=district) | Q(category__iexact=district) | Q(url_city__iexact=district)
    ).order_by("-date")
    
    page_obj = Paginator(news_list, 15).get_page(request.GET.get('page'))
    return render(request, "mynews/district_news.html", {
        "district": district, 
        "page_obj": page_obj, 
        "news_count": news_list.count(), 
        **get_common_sidebar_data()
    })

# --- API & SEO ---
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

def sitemap_xml(request):
    items = News.objects.filter(status='Published').order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        city = n.url_city if n.url_city else 'news'
        full_url = f"{SITE_URL.rstrip('/')}/{city}/{n.slug}/"
        xml += f'<url><loc>{full_url}</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    xml += '</urlset>'
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request): 
    return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")

def ads_txt(request): 
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

# Legal Pages
def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
