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

# --- 1. HOME PAGE UPDATED ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status='Published').order_by("-date")
        
        # --- Section-wise Data Fetching (Har section ke liye 5 posts) ---
        
        # 1. International (Sabse Upar)
        international_news = all_news.filter(district__iexact="International")[:5]
        
        # 2. National + Delhi + Other States
        national_labels = ['National', 'Delhi', 'Other-States']
        national_news = all_news.filter(district__in=national_labels)[:5]

        # 3. UP NEWS (Excluded non-up labels)
        non_up_labels = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market']
        up_news_qs = all_news.exclude(district__in=non_up_labels).exclude(district__isnull=True)[:5]

        # 4. Entertainment (Bollywood + Hollywood)
        ent_labels = ['Bollywood', 'Hollywood']
        entertainment_news = all_news.filter(district__in=ent_labels)[:5]

        # 5. Technology + Market
        tech_market_labels = ['Technology', 'Market']
        tech_market_news = all_news.filter(district__in=tech_market_labels)[:5]

        # 6. Sports
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
        
# --- DETAIL VIEW ---
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug=slug)
    v_id = None
    
    # Cloudinary Optimized OG Image for Social Sharing
    raw_img = news.image_url if news.image_url else (news.image.url if news.image else None)
    # 1200x630 is the standard for Facebook/WhatsApp sharing
    og_image = f"https://res.cloudinary.com/dbe9v8mca/image/fetch/f_auto,q_auto,w_1200,h_630,c_fill/{raw_img}" if raw_img else None
    
    if news.youtube_url:
        regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?|shorts)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
        match = re.search(regex, news.youtube_url)
        if match:
            v_id = match.group(1)
    
    context = {
        "news": news,
        "v_id": v_id,
        "og_title": news.title,
        "og_image": og_image,
        "related_news": News.objects.filter(district=news.district, status='Published').exclude(id=news.id).order_by("-date")[:6],
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- DISTRICT VIEW ---
def district_news(request, district):
    news_list = News.objects.filter(status='Published').filter(
        Q(district__iexact=district) | Q(url_city__iexact=district)
    ).order_by("-date")
    
    return render(request, "mynews/district_news.html", {
        "district": district, 
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get('page')), 
        **get_common_sidebar_data()
    })

# --- UTILS (Sitemap, Robots, Ads) ---
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

# --- STATIC PAGES ---
def privacy_policy(request): 
    return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())

def about_us(request): 
    return render(request, "mynews/about_ us.html", get_common_sidebar_data())

def contact_us(request): 
    return render(request, "mynews/contact_us.html", get_common_sidebar_data())

def disclaimer(request): 
    return render(request, "mynews/disclaimer.html", get_common_sidebar_data())

