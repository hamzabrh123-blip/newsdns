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

# --- Common Sidebar Data ---
def get_common_sidebar_data():
    published = News.objects.filter(status='Published')
    used_districts = published.values_list('district', flat=True).distinct()
    dynamic_cities = []

    # Sidebar categories exclusion
    exclude_keys = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi', 'Other-States']

    for eng, hin, cat_slug in LOCATION_DATA:
        if eng in used_districts and eng not in exclude_keys:
            dynamic_cities.append({'id': eng, 'name': hin})

    return {
        "up_sidebar": published.order_by("-date")[:10],
        "bharat_sidebar": published.filter(Q(category__icontains="राष्ट्रीय") | Q(district="National"))[:5],
        "world_sidebar": published.filter(Q(category__icontains="अंतर्राष्ट्रीय") | Q(district="International"))[:5],
        "bazaar_sidebar": published.filter(Q(category__icontains="मार्केट") | Q(district="Market"))[:5],
        "sports_sidebar": published.filter(Q(category__icontains="खेल") | Q(district="Sports"))[:5],
        "dynamic_up_cities": dynamic_cities,
    }

# --- 1. HOME PAGE (SECTION WISE) ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status='Published').order_by("-date")
        
        # Ye labels UP section se National/World ko bahar nikalne ke liye hain
        exclude_labels = [
            'National', 'International', 'Sports', 'Bollywood', 'Technology', 'Market',
            'राष्ट्रीय खबर', 'अंतर्राष्ट्रीय', 'खेल समाचार', 'Bollywood', 'मार्केट भाव', 'टेक्नोलॉजी',
            'Bharat', 'World', 'देश / भारत', 'दुनिया / विदेश'
        ]
        
        # Logic: UP news mein sirf wahi aayega jo National/World nahi hai
        up_news_qs = all_news.exclude(
            Q(category__in=exclude_labels) | 
            Q(district__in=exclude_labels) |
            Q(category__icontains="राष्ट्रीय") |
            Q(category__icontains="अंतर्राष्ट्रीय")
        )

        context = {
            "top_5_highlights": all_news.filter(show_in_highlights=True)[:5],
            
            # 1. UP News Section (Sirf Districts/UP news)
            "up_news": up_news_qs[:12], 
            
            # 2. National Section
            "national_news": all_news.filter(Q(category__icontains="राष्ट्रीय") | Q(district="National") | Q(category__icontains="Bharat"))[:4],
            
            # 3. World Section
            "world_news": all_news.filter(Q(category__icontains="अंतर्राष्ट्रीय") | Q(district="International") | Q(category__icontains="World"))[:4],
            
            # 4. Entertainment & Others
            "bollywood_news": all_news.filter(Q(category__icontains="बॉलीवुड") | Q(district="Bollywood"))[:4],
            "sports_news": all_news.filter(Q(category__icontains="खेल") | Q(district="Sports"))[:4],
            
            # Pagination ke liye sari news mix chalti rahegi niche
            "other_news": Paginator(all_news, 10).get_page(request.GET.get('page')),
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse(f"System Update in Progress... Error details: {e}")

# --- 2. NEWS DETAIL ---
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
        "related_news": News.objects.filter(category=news.category, status='Published').exclude(id=news.id).order_by("-date")[:6],
        "v_id": v_id,
        "meta_description": strip_tags(news.content)[:160] if news.content else news.title,
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT / CATEGORY PAGE ---
def district_news(request, district):
    news_list = News.objects.filter(status='Published').filter(
        Q(district__iexact=district) | Q(category__icontains=district) | Q(url_city__iexact=district)
    ).order_by("-date")
    
    page_obj = Paginator(news_list, 15).get_page(request.GET.get('page'))
    
    return render(request, "mynews/district_news.html", {
        "district": district, 
        "page_obj": page_obj, 
        "news_count": news_list.count(), 
        **get_common_sidebar_data()
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
