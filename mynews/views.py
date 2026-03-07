import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .utils import extract_video_id
from .models import News, SidebarWidget 

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"

# --- 1. COMMON DATA (Sidebar & Footer) ---
def get_common_sidebar_data():
    """साइडबार के लिए डेटा लोड करना"""
    published = News.objects.filter(status='Published')
    sidebar_widgets = SidebarWidget.objects.filter(active=True).order_by('order')
    
    return {
        "sidebar_widgets": sidebar_widgets,
        "up_sidebar": published.exclude(district__in=['International', 'Sports', 'Market']).order_by("-date")[:10],
        "world_sidebar": published.filter(district__iexact="International").order_by("-date")[:5],
        "bazaar_sidebar": published.filter(district__iexact="Market").order_by("-date")[:5],
        "sports_sidebar": published.filter(district__iexact="Sports").order_by("-date")[:5],
    }

# --- 2. HOME PAGE ---
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
            "meta_description": "Uttar World News: उत्तर प्रदेश, भारत और दुनिया की ताज़ा ब्रेकिंग न्यूज़ और लाइव अपडेट।",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse("सर्वर में समस्या है, कृपया बाद में प्रयास करें।")

# --- 3. NEWS DETAIL PAGE (SEO + Related News) ---
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug=slug)
    video_url = news.youtube_url.strip() if news.youtube_url else None
    v_id = extract_video_id(video_url)
    
    # स्मार्ट रिलेटेड न्यूज़ लॉजिक
    related_news = News.objects.filter(status='Published', district=news.district).exclude(id=news.id).order_by('-date')[:6]
    
    if related_news.count() < 4:
        category_news = News.objects.filter(status='Published', category=news.category).exclude(id=news.id).exclude(id__in=[n.id for n in related_news]).order_by('-date')[:6 - related_news.count()]
        related_news = list(related_news) + list(category_news)

    # SEO Description (Content से HTML हटाकर 160 अक्षर)
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

# --- 4. DISTRICT/CATEGORY VIEW (H1 & 70 Words Ready) ---
def district_news(request, district):
    # URL से डैश हटाकर साफ नाम निकालें
    clean_district = district.replace('-', ' ')
    
    if clean_district.lower() in ['uttar pradesh', 'up news', 'up']:
        exclude_cats = ['International', 'National', 'Sports', 'Market', 'Technology', 'Bollywood', 'Hollywood']
        news_list = News.objects.filter(status='Published').exclude(district__in=exclude_cats).order_by("-date")
        meta_desc = f"उत्तर प्रदेश (UP) की ताज़ा खबरें: राजनीति, अपराध, और स्थानीय समाचारों का पूरा कवरेज।"
    else:
        news_list = News.objects.filter(status='Published').filter(
            Q(district__iexact=clean_district) | 
            Q(url_city__iexact=district) | 
            Q(category__iexact=clean_district)
        ).order_by("-date")
        meta_desc = f"{clean_district} न्यूज़: {clean_district} की ताज़ा खबरें और लाइव मुख्य समाचार विस्तार से पढ़ें।"
    
    # 70 शब्दों के कंटेंट के लिए 20 न्यूज़ प्रति पेज (परफॉरमेंस के लिए बेस्ट है)
    paginator = Paginator(news_list, 20) 
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, "mynews/district_news.html", {
        "district": clean_district, 
        "page_obj": page_obj, 
        "meta_description": meta_desc,
        **get_common_sidebar_data()
    })

# --- 5. API & SEO FILES ---
def fb_news_api(request):
    """Bulk Posting Script के लिए API"""
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
        city_path = n.url_city if n.url_city else "news"
        xml += f'<url><loc>{SITE_URL.rstrip("/")}/{city_path}/{n.slug}/</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    return HttpResponse(xml + '</urlset>', content_type="application/xml")

def robots_txt(request): 
    return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")

def ads_txt(request): 
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

# --- 6. STATIC PAGES ---
def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
