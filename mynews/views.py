import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .utils import extract_video_id
from .models import News, SidebarWidget 

logger = logging.getLogger(__name__)

# पक्का करें कि यहाँ अंत में / न हो
SITE_URL = "https://uttarworld.com"

# --- 1. COMMON DATA (Sidebar & Footer) ---
def get_common_sidebar_data():
    """साइडबार के लिए डेटा लोड करना - Try-Except के साथ सुरक्षित"""
    try:
        published = News.objects.filter(status='Published')
        sidebar_widgets = SidebarWidget.objects.filter(active=True).order_by('order')
        
        return {
            "sidebar_widgets": sidebar_widgets,
            "up_sidebar": published.exclude(district__in=['International', 'Sports', 'Market', 'National', 'Bollywood', 'Technology']).order_by("-date")[:10],
            "world_sidebar": published.filter(district__iexact="International").order_by("-date")[:5],
            "bazaar_sidebar": published.filter(district__iexact="Market").order_by("-date")[:5],
            "sports_sidebar": published.filter(district__iexact="Sports").order_by("-date")[:5],
        }
    except Exception as e:
        logger.error(f"Sidebar Data Error: {e}")
        return {
            "sidebar_widgets": [],
            "up_sidebar": [],
            "world_sidebar": [],
            "bazaar_sidebar": [],
            "sports_sidebar": [],
        }

# --- 2. HOME PAGE ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status='Published').order_by("-date")
        
        # कैटेगरी फिल्टरिंग
        international_news = all_news.filter(district__iexact="International")[:7]
        national_labels = ['National', 'Delhi', 'Other-States']
        national_news = all_news.filter(district__in=national_labels)[:13]

        non_up_labels = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi']
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
            "meta_description": "Uttar World News: उत्तर प्रदेश, भारत और दुनिया की ताज़ा ब्रेकिंग न्यूज़ और लाइव अपडेट।",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse(f"सर्वर में समस्या है: {e}", status=500)

# --- 3. SEO & TEXT FILES ---
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Allow: /",
        f"Sitemap: {SITE_URL}/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def ads_txt(request): 
    content = "google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    try:
        items = News.objects.filter(status='Published').order_by('-date')[:500]
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for n in items:
            city_path = n.url_city if n.url_city else "news"
            xml += f'  <url>\n    <loc>{SITE_URL.rstrip("/")}/{city_path}/{n.slug}/</loc>\n    <lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod>\n  </url>\n'
        xml += '</urlset>'
        return HttpResponse(xml, content_type="application/xml")
    except Exception as e:
        return HttpResponse(str(e), content_type="text/plain")

# --- 4. NEWS DETAIL ---
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug=slug)
    v_id = extract_video_id(news.youtube_url) if news.youtube_url else None
    
    related_news = News.objects.filter(status='Published', district=news.district).exclude(id=news.id).order_by('-date')[:6]
    
    clean_text = re.sub('<[^<]+?>', '', news.content) if news.content else ""
    meta_desc = (clean_text[:157] + '...') if len(clean_text) > 160 else clean_text

    context = {
        "news": news,
        "v_id": v_id,
        "related_news": related_news, 
        "meta_description": meta_desc or news.title,
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 5. CATEGORY/DISTRICT PAGE (FIXED FOR UP) ---
def district_news(request, district):
    # '-' को स्पेस में बदलें (जैसे Uttar-Pradesh -> Uttar Pradesh)
    clean_district = district.replace('-', ' ')
    
    all_published = News.objects.filter(status='Published')

    # अगर "Uttar Pradesh" पेज माँगा गया है, तो सभी जिलों की खबर दिखाओ
    if clean_district.lower() == 'uttar pradesh':
        non_up_labels = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi']
        news_list = all_published.exclude(district__in=non_up_labels).exclude(district__isnull=True).order_by("-date")
    else:
        # किसी खास जिले या कैटेगरी के लिए फ़िल्टर
        news_list = all_published.filter(
            Q(district__iexact=clean_district) | 
            Q(url_city__iexact=district) | 
            Q(category__iexact=clean_district)
        ).order_by("-date")
    
    paginator = Paginator(news_list, 20) 
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, "mynews/district_news.html", {
        "district": clean_district, 
        "page_obj": page_obj, 
        **get_common_sidebar_data()
    })

# --- 6. OTHER VIEWS ---
def fb_news_api(request):
    news_list = News.objects.filter(status='Published').order_by('-date')[:20]
    data = [{'id': n.id, 'title': n.title, 'url': f"{SITE_URL}/{n.url_city or 'news'}/{n.slug}/"} for n in news_list]
    return JsonResponse(data, safe=False)

def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
