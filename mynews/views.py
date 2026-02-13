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

# --- Common Sidebar Data (Fixed for all sections) ---
def get_common_sidebar_data():
    published = News.objects.filter(status='Published')
    used_districts = published.values_list('district', flat=True).distinct()
    dynamic_cities = []

    # Inhe Districts sidebar list mein nahi dikhana hai
    exclude_keys = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Entertainment']

    for eng, hin, cat_slug in LOCATION_DATA:
        if eng in used_districts and eng not in exclude_keys:
            dynamic_cities.append({'id': eng, 'name': hin})

    return {
        "up_sidebar": published.order_by("-date")[:10],
        # EXACT FILTER: Overlap khatam karne ke liye
        "bharat_sidebar": published.filter(Q(category="National") | Q(district="National"))[:5],
        "world_sidebar": published.filter(Q(category="International") | Q(district="International"))[:5],
        "bazaar_sidebar": published.filter(Q(category="Market") | Q(district="Market"))[:5],
        "sports_sidebar": published.filter(Q(category="Sports") | Q(district="Sports"))[:5],
        "dynamic_up_cities": dynamic_cities,
    }

# --- 1. HOME PAGE (All Sections Fixed & Separate) ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status='Published').order_by("-date")
        
        # Current page number check karo
        page_number = request.GET.get('page', 1)
        
        # Paginator for 'Other News' section
        paginator = Paginator(all_news, 12) # Ek page par 12 news
        other_news_page = paginator.get_page(page_number)
        
        exclude_cats = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market']
        
        context = {
                    # Agar page 1 hai toh sab dikhao, agar page 2+ hai toh sirf Pagination wali list dikhao
                    "top_5_highlights": all_news.filter(show_in_highlights=True)[:5] if page_number in [1, '1'] else None,
                    "national_news": all_news.filter(category="National")[:4] if page_number in [1, '1'] else None,
                    "world_news": all_news.filter(category="International")[:4] if page_number in [1, '1'] else None,
                    "up_news": all_news.exclude(category__in=exclude_cats)[:12] if page_number in [1, '1'] else None,
                    "entertainment_news": all_news.filter(category__in=['Bollywood', 'Hollywood'])[:6] if page_number in [1, '1'] else None,
                    "bazaar_news": all_news.filter(category="Market")[:4] if page_number in [1, '1'] else None,
    
                    # Ye hamesha dikhega aur badlega
                    "other_news": other_news_page, 
                    "page_number": int(page_number), # Template mein condition lagane ke liye
                    **common_data
                }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse("System Update in Progress...")

# --- 2. NEWS DETAIL ---
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug=slug, status='Published')
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([a-zA-Z0-9_-]{11})", news.youtube_url)
        if match: v_id = match.group(1)

    context = {
        "news": news,
        "v_id": v_id,
        "related_news": News.objects.filter(category=news.category, status='Published').exclude(id=news.id).order_by("-date")[:6],
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT / CATEGORY ---
def district_news(request, district):
    # Strict matching taaki URL se sahi news khule
    news_list = News.objects.filter(status='Published').filter(
        Q(district__iexact=district) | Q(category__iexact=district) | Q(url_city__iexact=district)
    ).order_by("-date")
    
    page_obj = Paginator(news_list, 15).get_page(request.GET.get('page'))
    return render(request, "mynews/district_news.html", {
        "district": district, "page_obj": page_obj, "news_count": news_list.count(), **get_common_sidebar_data()
    })

# --- SEO & LEGAL ---
def sitemap_xml(request):
    items = News.objects.filter(status='Published').order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        city = n.url_city if n.url_city else 'news'
        xml += f'<url><loc>{SITE_URL.rstrip("/")}/{city}/{n.slug}/</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    xml += '</urlset>'
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request): return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")
def ads_txt(request): return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
