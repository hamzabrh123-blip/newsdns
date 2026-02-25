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

# --- Common Sidebar Data ---
def get_common_sidebar_data():
    published = News.objects.filter(status='Published')
    used_districts = published.values_list('district', flat=True).distinct()
    dynamic_cities = []

    exclude_keys = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi', 'Other-States']

    for eng, hin, cat_slug in LOCATION_DATA:
        if eng in used_districts and eng not in exclude_keys:
            dynamic_cities.append({'id': eng, 'name': hin})

    return {
        "up_sidebar": published.exclude(district__in=['International', 'Sports', 'Market']).order_by("-date")[:10],
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
        
        # Section-wise Data logic
        international_news = all_news.filter(district__iexact="International")[:5]
        national_labels = ['National', 'Delhi', 'Other-States']
        national_news = all_news.filter(district__in=national_labels)[:5]

        non_up_labels = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market']
        up_news_qs = all_news.exclude(district__in=non_up_labels).exclude(district__isnull=True)[:5]

        context = {
            "top_5_highlights": all_news.filter(show_in_highlights=True)[:5],
            "international_news": international_news,
            "national_news": national_news,
            "up_news": up_news_qs, 
            "entertainment_news": all_news.filter(district__in=['Bollywood', 'Hollywood']).order_by("-date")[:5],
            "tech_market_news": all_news.filter(district__in=['Technology', 'Market']).order_by("-date")[:5],
            "sports_news": all_news.filter(district__iexact="Sports")[:5],
            "other_news": Paginator(all_news, 10).get_page(request.GET.get('page')),
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse(f"Server Error: {e}")
        
# --- 2. DETAIL VIEW ---
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug=slug)
    v_id = None
    
    # Cloudinary/Social Image Logic
    raw_img = news.image_url if news.image_url else (news.image.url if news.image else None)
    og_image = f"https://res.cloudinary.com/dbe9v8mca/image/fetch/f_auto,q_auto,w_1200,h_630,c_fill/{raw_img}" if raw_img else None
    
    # YouTube Logic
    if news.youtube_url:
        regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
        match = re.search(regex, news.youtube_url)
        if match: v_id = match.group(1)
    
    context = {
        "news": news,
        "v_id": v_id,
        "og_title": news.title,
        "og_image": og_image,
        "related_news": News.objects.filter(status='Published').exclude(id=news.id).order_by('?')[:6],
        "meta_description": news.content[:160],
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT/CATEGORY VIEW (UP News Fix) ---
def district_news(request, district):
    # Fix: Dash ko replace karna aur UP News ko handle karna
    clean_district = district.replace('-', ' ')
    
    # Agar user 'Uttar Pradesh' ya 'UP-News' mang raha hai
    if clean_district.lower() in ['uttar pradesh', 'up news']:
        # Wo saari news jo International/National/Sports/Market/Tech/Bollywood nahi hain
        exclude_cats = ['International', 'National', 'Sports', 'Market', 'Technology', 'Bollywood', 'Hollywood']
        news_list = News.objects.filter(status='Published').exclude(district__in=exclude_cats).order_by("-date")
    else:
        # Baaki normal districts ke liye
        news_list = News.objects.filter(status='Published').filter(
            Q(district__iexact=clean_district) | 
            Q(url_city__iexact=district) | 
            Q(category__iexact=clean_district)
        ).order_by("-date")
    
    paginator = Paginator(news_list, 30) 
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, "mynews/district_news.html", {
        "district": clean_district, 
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

def robots_txt(request): 
    return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")

def ads_txt(request): 
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_ us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())

