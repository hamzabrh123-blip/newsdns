import re, logging
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils.timezone import now
from django.utils.html import escape, strip_tags
from .models import News, SidebarWidget 

logger = logging.getLogger(__name__)

SITE_URL = "https://uttarworld.com"

# --- 1. COMMON DATA (AdSense Friendly) ---
def get_common_sidebar_data():
    try:
        # केवल Published खबरें ही साइडबार में आएं
        published = News.objects.filter(status='Published').order_by("-date")
        sidebar_widgets = SidebarWidget.objects.filter(active=True).order_by('order')
        
        non_up_labels = ['International', 'National', 'Sports', 'Market', 'Bollywood', 'Hollywood', 'Technology', 'Delhi']
        up_side = published.exclude(district__in=non_up_labels).exclude(district__isnull=True)[:10]

        return {
            "sidebar_widgets": sidebar_widgets,
            "up_sidebar": up_side,
            "world_sidebar": published.filter(district__iexact="International")[:5],
            "bazaar_sidebar": published.filter(district__iexact="Market")[:5],
            "sports_sidebar": published.filter(district__iexact="Sports")[:5],
        }
    except Exception as e:
        logger.error(f"Sidebar Data Error: {e}")
        return {"sidebar_widgets": [], "up_sidebar": [], "world_sidebar": [], "bazaar_sidebar": [], "sports_sidebar": []}

# --- 2. HOME PAGE ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status='Published').order_by("-date")
        
        # AdSense के लिए होमपेज पर पर्याप्त कंटेंट सुनिश्चित करना
        context = {
            "top_5_highlights": all_news.filter(show_in_highlights=True)[:11],
            "international_news": all_news.filter(district__iexact="International")[:7],
            "national_news": all_news.filter(district__in=['National', 'Delhi', 'Other-States'])[:13],
            "up_news": all_news.exclude(district__in=['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi']).exclude(district__isnull=True)[:37], 
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
        return redirect('/') # होमपेज पर भी एरर आए तो रिफ्रेश या रीडायरेक्ट करें

# --- 3. NEWS DETAIL (The Safety Shield) ---
def news_detail(request, url_city, slug):
    try:
        # 404 के बजाय filter().first() का इस्तेमाल ताकि क्रैश न हो
        news = News.objects.filter(slug=slug, status='Published').first()

        # अगर न्यूज नहीं मिली (गलत स्लग) तो सीधा होमपेज पर रीडायरेक्ट
        if not news:
            return redirect('home', permanent=True)

        related_news = News.objects.filter(status='Published').filter(
            Q(district=news.district) | Q(category=news.category)
        ).exclude(id=news.id).order_by('-date')[:6]
        
        context = {
            "news": news,
            "related_news": related_news, 
            "meta_description": strip_tags(news.content[:160]), # Meta साफ़ रखें
            **get_common_sidebar_data()
        }
        return render(request, "mynews/news_detail.html", context)
    
    except Exception as e:
        return redirect('home')

# --- 4. DISTRICT PAGE (Galti-Proof) ---
def district_news(request, district):
    clean_district = district.replace('-', ' ')
    all_published = News.objects.filter(status='Published')

    # अगर जिला खाली है या गलत है, तो 404 के बजाय होमपेज
    news_list = all_published.filter(
        Q(district__iexact=clean_district) | 
        Q(url_city__iexact=district) | 
        Q(category__iexact=clean_district)
    ).order_by("-date")

    if not news_list.exists() and clean_district.lower() != 'uttar pradesh':
        return redirect('home')

    if clean_district.lower() == 'uttar pradesh':
        non_up_labels = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi']
        news_list = all_published.exclude(district__in=non_up_labels).exclude(district__isnull=True).order_by("-date")
    
    paginator = Paginator(news_list, 20) 
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, "mynews/district_news.html", {
        "district": clean_district, 
        "page_obj": page_obj, 
        **get_common_sidebar_data()
    })

# --- 5. SEO & TEXT FILES (AdSense & Google Bot Friendly) ---
def robots_txt(request):
    lines = ["User-Agent: *", "Allow: /", "Disallow: /admin/", f"Sitemap: {SITE_URL}/sitemap.xml"]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def ads_txt(request): 
    content = "google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    try:
        items = News.objects.filter(status='Published').order_by('-date')[:2000] 
        xml_output = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n'
        xml_output += f'  <url>\n    <loc>{SITE_URL}/</loc>\n    <lastmod>{now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'
        
        for n in items:
            city_path = n.url_city.lower() if n.url_city else "news"
            loc = f'{SITE_URL}/{city_path}/{n.slug}/'
            xml_output += f'  <url>\n    <loc>{escape(loc)}</loc>\n    <lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod>\n'
            
            if n.youtube_url:
                clean_title = escape(strip_tags(n.title[:90]))
                clean_desc = escape(strip_tags(n.content[:200]))
                xml_output += f'    <video:video>\n      <video:title>{clean_title}</video:title>\n      <video:description>{clean_desc}</video:description>\n    </video:video>\n'
            
            xml_output += '  </url>\n'
        
        xml_output += '</urlset>'
        return HttpResponse(xml_output, content_type="application/xml")
    except:
        return redirect('/')

# --- 6. UTILITIES ---
def fb_news_api(request):
    news_list = News.objects.filter(status='Published').order_by('-date')[:20]
    data = [{'id': n.id, 'title': n.title, 'url': f"{SITE_URL}/{n.url_city.lower() if n.url_city else 'news'}/{n.slug}/"} for n in news_list]
    return JsonResponse(data, safe=False)

def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
