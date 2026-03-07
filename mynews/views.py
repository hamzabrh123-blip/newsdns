import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .utils import extract_video_id
from .models import News, SidebarWidget 

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
    sidebar_widgets = SidebarWidget.objects.filter(active=True).order_by('order')
    
    return {
        "sidebar_widgets": sidebar_widgets,
        "up_sidebar": published.exclude(district__in=['International', 'Sports', 'Market']).order_by("-date")[:10],
        "world_sidebar": published.filter(district__iexact="International").order_by("-date")[:5],
        "bazaar_sidebar": published.filter(district__iexact="Market").order_by("-date")[:5],
        "sports_sidebar": published.filter(district__iexact="Sports").order_by("-date")[:5],
    }

# --- 1. HOME PAGE ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status='Published').order_by("-date")
        
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
            "entertainment_news": all_news.filter(district__in=['Bollywood', 'Hollywood'])[:10],
            "market_news": all_news.filter(district__iexact='Market')[:8],
            "tech_news": all_news.filter(district__iexact='Technology')[:8],
            "sports_news": all_news.filter(district__iexact="Sports")[:8],
            "other_news": Paginator(all_news, 10).get_page(request.GET.get('page')),
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse("Server Error")

# --- 2. NEWS DETAIL PAGE (FIXED FOR SMART RELATED NEWS) ---
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug=slug)
    video_url = news.youtube_url.strip() if news.youtube_url else None
    v_id = extract_video_id(video_url)
    
    # स्मार्ट फ़िल्टर: पहले उसी जिला (District) की खबरें खोजो जो अभी पढ़ी जा रही है
    related_news = News.objects.filter(
        status='Published', 
        district=news.district
    ).exclude(id=news.id).order_by('-date')[:6]
    
    # अगर उस जिला में ज्यादा खबरें नहीं हैं, तो उसी कैटेगरी (Category) की खबरें उठाओ
    if related_news.count() < 4:
        category_news = News.objects.filter(
            status='Published',
            category=news.category
        ).exclude(id=news.id).exclude(id__in=[n.id for n in related_news]).order_by('-date')[:6 - related_news.count()]
        related_news = list(related_news) + list(category_news)

    # अगर फिर भी खबरें कम हैं (जैसे नई कैटेगरी), तो लेटेस्ट ताज़ा खबरें दिखा दो
    if len(related_news) < 4:
        latest_news = News.objects.filter(status='Published').exclude(id=news.id).exclude(id__in=[n.id for n in related_news]).order_by('-date')[:6 - len(related_news)]
        related_news = list(related_news) + list(latest_news)
    
    context = {
        "news": news,
        "v_id": v_id,
        "related_news": related_news, 
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT/CATEGORY VIEW ---
def district_news(request, district):
    clean_district = district.replace('-', ' ')
    if clean_district.lower() in ['uttar pradesh', 'up news']:
        exclude_cats = ['International', 'National', 'Sports', 'Market', 'Technology', 'Bollywood', 'Hollywood']
        news_list = News.objects.filter(status='Published').exclude(district__in=exclude_cats).order_by("-date")
    else:
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

# --- 4. SEO VIEWS ---
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

# --- 5. STATIC PAGES ---
def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
