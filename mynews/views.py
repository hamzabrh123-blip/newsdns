import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils.timezone import now # इसे जोड़ना मत भूलना
from .models import News, SidebarWidget 

logger = logging.getLogger(__name__)

# पक्का करें कि यहाँ अंत में / न हो
SITE_URL = "https://uttarworld.com"

# --- 1. COMMON DATA (Sidebar & Footer) ---
def get_common_sidebar_data():
    try:
        published = News.objects.filter(status='Published').order_by("-date")
        sidebar_widgets = SidebarWidget.objects.filter(active=True).order_by('order')
        
        # यूपी साइडबार लॉजिक
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
        
        # Categories
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
    lines = ["User-Agent: *", "Allow: /", "Disallow: /admin/", f"Sitemap: {SITE_URL}/sitemap.xml"]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def ads_txt(request): 
    content = "google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    try:
        # ताज़ा 2000 खबरें उठाएं
        items = News.objects.filter(status='Published').order_by('-date')[:2000] 
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        # यहाँ हमने video schema का Namespace (xmlns:video) जोड़ दिया है
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n'
        
        # 1. Homepage
        xml += f'  <url>\n    <loc>{SITE_URL.rstrip("/")}/</loc>\n    <lastmod>{now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'
        
        # 2. News Items
        for n in items:
            city_path = n.url_city.lower() if n.url_city else "news"
            loc = f'{SITE_URL.rstrip("/")}/{city_path}/{n.slug}/'
            
            xml += '  <url>\n'
            xml += f'    <loc>{loc}</loc>\n'
            xml += f'    <lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod>\n'
            
            # --- VIDEO SITEMAP LOGIC START ---
            if n.youtube_url:
                # थंबनेल के लिए आपकी न्यूज़ इमेज ही काम आएगी
                thumbnail = n.image_url if n.image_url else f"{SITE_URL}/static/districts/news.webp"
                if n.image and not n.image_url:
                    thumbnail = f"{SITE_URL}{n.image.url}"

                xml += '    <video:video>\n'
                xml += f'      <video:thumbnail_loc>{thumbnail}</video:thumbnail_loc>\n'
                xml += f'      <video:title>{n.title[:90]}</video:title>\n'
                xml += f'      <video:description>{n.content[:200]|striptags}</video:description>\n'
                xml += f'      <video:content_loc>{n.youtube_url}</video:content_loc>\n'
                # Embed URL बनाना (GSC इसे पसंद करता है)
                video_id = ""
                if "v=" in n.youtube_url: video_id = n.youtube_url.split("v=")[1].split("&")[0]
                elif "youtu.be/" in n.youtube_url: video_id = n.youtube_url.split("youtu.be/")[1].split("?")[0]
                
                if video_id:
                    xml += f'      <video:player_loc>https://www.youtube.com/embed/{video_id}</video:player_loc>\n'
                
                xml += f'      <video:publication_date>{n.date.strftime("%Y-%m-%dT%H:%M:%S+05:30")}</video:publication_date>\n'
                xml += '      <video:family_friendly>yes</video:family_friendly>\n'
                xml += '    </video:video>\n'
            # --- VIDEO SITEMAP LOGIC END ---

            xml += '  </url>\n'
            
        xml += '</urlset>'
        return HttpResponse(xml, content_type="application/xml")
    except Exception as e:
        logger.error(f"Sitemap Error: {e}")
        return HttpResponse(f"Error generating sitemap", content_type="text/plain")
        
# --- 4. NEWS DETAIL ---
def news_detail(request, url_city, slug):
    # url_city को ignore कर सकते हैं क्योंकि slug unique है, 
    # लेकिन SEO के लिए URL में city होना ज़रूरी है
    news = get_object_or_404(News, slug=slug)

    # रिलेटेड न्यूज़: उसी जिले या कैटेगरी की खबरें
    related_news = News.objects.filter(status='Published').filter(
        Q(district=news.district) | Q(category=news.category)
    ).exclude(id=news.id).order_by('-date')[:6]
    
    context = {
        "news": news,
        "related_news": related_news, 
        "meta_description": news.title[:160], # डिस्क्रिप्शन को लिमिट करना अच्छा है
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 5. DISTRICT PAGE ---
def district_news(request, district):
    clean_district = district.replace('-', ' ')
    all_published = News.objects.filter(status='Published')

    if clean_district.lower() == 'uttar pradesh':
        non_up_labels = ['National', 'International', 'Sports', 'Bollywood', 'Hollywood', 'Technology', 'Market', 'Delhi']
        news_list = all_published.exclude(district__in=non_up_labels).exclude(district__isnull=True).order_by("-date")
    else:
        # District, Category या URL City तीनों में से कहीं भी मैच हो जाए
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
    data = [{'id': n.id, 'title': n.title, 'url': f"{SITE_URL}/{n.url_city.lower() if n.url_city else 'news'}/{n.slug}/"} for n in news_list]
    return JsonResponse(data, safe=False)

# Standard Pages
def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
