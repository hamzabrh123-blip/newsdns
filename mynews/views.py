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

    exclude_keys = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi', 'Other-States']

    for eng, hin, cat_slug in LOCATION_DATA:
        if eng in used_districts and eng not in exclude_keys:
            dynamic_cities.append({'id': eng, 'name': hin})

    return {
        # Sidebar mein latest 10 news (UP)
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
        
        # Section-wise Data
        international_news = all_news.filter(district__iexact="International")[:5]
        national_labels = ['National', 'Delhi', 'Other-States']
        national_news = all_news.filter(district__in=national_labels)[:5]

        non_up_labels = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market']
        up_news_qs = all_news.exclude(district__in=non_up_labels).exclude(district__isnull=True)[:5]

        ent_labels = ['Bollywood', 'Hollywood']
        entertainment_news = all_news.filter(district__in=ent_labels)[:5]

        tech_market_labels = ['Technology', 'Market']
        tech_market_news = all_news.filter(district__in=tech_market_labels)[:5]

        sports_news = all_news.filter(district__iexact="Sports")[:5]

        context = {
            "top_5_highlights": all_news.filter(show_in_highlights=True)[:5],
            "international_news": international_news,
            "national_news": national_news,
            "up_news": up_news_qs, 
            "entertainment_news": entertainment_news,
            "tech_market_news": tech_market_news,
            "sports_news": sports_news,
            "other_news": Paginator(all_news, 10).get_page(request.GET.get('page')),
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse(f"Server Error: {e}")
        
# --- DETAIL VIEW (With Random Related News) ---
def news_detail(request, url_city, slug):
    # 1. Fetch News
    news = get_object_or_404(News, slug=slug)
    v_id = None
    
    # 2. SEO & Social Sharing (WhatsApp/FB ke liye badi photo)
    raw_img = news.image_url if news.image_url else (news.image.url if news.image else None)
    # Cloudinary optimization for social preview (1200x630 standard size)
    og_image = f"https://res.cloudinary.com/dbe9v8mca/image/fetch/f_auto,q_auto,w_1200,h_630,c_fill/{raw_img}" if raw_img else None
    
    # 3. YouTube Logic
    if news.youtube_url:
        regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
        match = re.search(regex, news.youtube_url)
        if match:
            v_id = match.group(1)
    
    # 4. RANDOM RELATED NEWS (Jo aapne manga tha)
    # Isse har refresh par niche ki news badalti rahegi
    related_random = News.objects.filter(status='Published').exclude(id=news.id).order_by('?')[:6]
    
    context = {
        "news": news,
        "v_id": v_id,
        "og_title": news.title,
        "og_image": og_image,
        "related_news": related_random,
        "meta_description": news.content[:160], # Search engines ke liye
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- DISTRICT VIEW (Now with 30 News per page) ---
def district_news(request, district):
    news_list = News.objects.filter(status='Published').filter(
        Q(district__iexact=district) | Q(url_city__iexact=district)
    ).order_by("-date")
    
    # Yahan 15 ko badal kar 30 kar diya gaya hai
    paginator = Paginator(news_list, 30) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "mynews/district_news.html", {
        "district": district, 
        "page_obj": page_obj, 
        **get_common_sidebar_data()
    })

# --- UTILS & STATIC PAGES ---
def sitemap_xml(request):
    items = News.objects.filter(status='Published').order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        xml += f'<url><loc>{SITE_URL.rstrip("/")}/{n.url_city or "news"}/{n.slug}/</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    return HttpResponse(xml + '</urlset>', content_type="application/xml")

def robots_txt(request): 
    return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")

def ads_txt(request): 
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def privacy_policy(request): 
    return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())

def about_us(request): 
    return render(request, "mynews/about_ us.html", get_common_sidebar_data())

def contact_us(request): 
    return render(request, "mynews/contact_us.html", get_common_sidebar_data())

def disclaimer(request): 
    return render(request, "mynews/disclaimer.html", get_common_sidebar_data())

