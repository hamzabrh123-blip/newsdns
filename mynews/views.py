import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils.html import strip_tags

from .models import News
from .constants import LOCATION_DATA

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"

# --- Common Sidebar Data (CLEAN LOGIC) ---
def get_common_sidebar_data():
    published = News.objects.filter(status='Published')
    used_districts = published.values_list('district', flat=True).distinct()
    
    # Inhe hum 'zila' wale section mein kabhi nahi dikhayenge
    exclude_keys = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi', 'Other-States']
    
    dynamic_cities = []
    for eng, hin, cat_slug in LOCATION_DATA:
        # Sirf tabhi add karo agar wo UP ka asli zila ho aur exclude list mein na ho
        if eng in used_districts and eng not in exclude_keys:
            dynamic_cities.append({'id': eng, 'name': hin})

    return {
        "up_sidebar": published.exclude(district__in=['International', 'Sports', 'Market', 'National']).order_by("-date")[:10],
        "bharat_sidebar": published.filter(district__iexact="National")[:5],
        "world_sidebar": published.filter(district__iexact="International")[:5],
        "bazaar_sidebar": published.filter(district__iexact="Market")[:5],
        "sports_sidebar": published.filter(district__iexact="Sports")[:5],
        "dynamic_up_cities": dynamic_cities,
    }

# --- 1. HOME PAGE ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status='Published').order_by("-date")
        
        # Section-wise filtering
        international_news = all_news.filter(district__iexact="International")[:7]
        national_labels = ['National', 'Delhi', 'Other-States']
        national_news = all_news.filter(district__in=national_labels)[:13]

        non_up_labels = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market']
        up_news_qs = all_news.exclude(district__in=non_up_labels).exclude(district__isnull=True)[:37]

        context = {
            "top_5_highlights": all_news.filter(show_in_highlights=True)[:11],
            "international_news": international_news,
            "national_news": national_news,
            "up_news": up_news_qs, 
            "entertainment_news": all_news.filter(district__in=['Bollywood', 'Hollywood']).order_by("-date")[:10],
            "tech_market_news": all_news.filter(district__in=['Technology', 'Market']).order_by("-date")[:9],
            "sports_news": all_news.filter(district__iexact="Sports")[:3],
            "other_news": Paginator(all_news, 10).get_page(request.GET.get('page')),
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse(f"Server Error")

# --- 2. DETAIL VIEW (YOUTUBE FIXED) ---
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug=slug)
    
    # YouTube ID extraction
    v_id = None
    if news.youtube_url:
        regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
        match = re.search(regex, news.youtube_url)
        if match: v_id = match.group(1)
    
    related_random = News.objects.filter(status='Published').exclude(id=news.id).order_by('?')[:6]
    
    context = {
        "news": news,
        "v_id": v_id,
        "related_news": related_random,
        "meta_description": strip_tags(news.content)[:160] if news.content else news.title,
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT/CATEGORY VIEW (ZILA HATAO LOGIC) ---
def district_news(request, district):
    # URL mein kuch bhi ho, hum saaf naam dikhayenge
    clean_val = district.replace('-', ' ')
    
    # Agar National/International wala URL hai toh "zila" word screen par na dikhe
    display_name = clean_val
    for eng, hin, slug in LOCATION_DATA:
        if eng.lower() == clean_val.lower():
            display_name = hin
            break

    news_list = News.objects.filter(status='Published').filter(
        Q(district__iexact=clean_val) | 
        Q(url_city__iexact=district) | 
        Q(category__iexact=clean_val)
    ).order_by("-date")
    
    # Special case for UP News
    if clean_val.lower() in ['uttar pradesh', 'up news', 'uttar-pradesh']:
        exclude_cats = ['International', 'National', 'Sports', 'Market', 'Technology', 'Bollywood', 'Hollywood']
        news_list = News.objects.filter(status='Published').exclude(district__in=exclude_cats).order_by("-date")
        display_name = "उत्तर प्रदेश"

    paginator = Paginator(news_list, 30) 
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, "mynews/district_news.html", {
        "district": display_name, 
        "page_obj": page_obj, 
        **get_common_sidebar_data()
    })

# --- 4. UTILS & SEO ---
def sitemap_xml(request):
    items = News.objects.filter(status='Published').order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        city_path = n.url_city if n.url_city else "news"
        xml += f'<url><loc>{SITE_URL.rstrip("/")}/{city_path}/{n.slug}/</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    return HttpResponse(xml + '</urlset>', content_type="application/xml")

def robots_txt(request): return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")
def ads_txt(request): return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
def fb_news_api(request): # Keep existing API logic
    pass
# (Privacy, About, Contact etc. same rahenge)
