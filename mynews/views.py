import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"

# --- Common Data Function (Sabse Safe Version) ---
def get_common_sidebar_data():
    # Hum directly context dictionary bhej rahe hain bina model constants ko touch kiye
    context_data = {
        "up_sidebar": News.objects.filter(category="UP").order_by("-date")[:10],
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:5],
        "world_sidebar": News.objects.filter(category="International").order_by("-date")[:5],
        "bazaar_sidebar": News.objects.filter(category="Market").order_by("-date")[:5],
        "sports_sidebar": News.objects.filter(category="Sports").order_by("-date")[:5],
        "dynamic_up_cities": [
            {'id': 'lucknow', 'name': 'लखनऊ'},
            {'id': 'kanpur', 'name': 'कानपुर'},
            {'id': 'varanasi', 'name': 'वाराणसी'},
            {'id': 'prayagraj', 'name': 'प्रयागराज'},
            {'id': 'gorakhpur', 'name': 'गोरखपुर'},
            {'id': 'ayodhya', 'name': 'अयोध्या'},
        ]
    }
    return context_data

# --- 1. HOME PAGE ---
def home(request):
    try:
        query = request.GET.get("q")
        common_data = get_common_sidebar_data()

        if query:
            news_list = News.objects.filter(title__icontains=query).order_by("-date")
            page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
            return render(request, "mynews/home.html", {"page_obj": page_obj, **common_data})
        
        all_important = News.objects.filter(is_important=True).order_by("-date")
        
        context = {
            "top_5_highlights": all_important[:5],
            "up_news": News.objects.filter(category="UP").order_by("-date")[:4],
            "national_news": News.objects.filter(category="National").order_by("-date")[:3],
            "world_news": News.objects.filter(category="International").order_by("-date")[:3],
            "other_news": Paginator(all_important[5:], 10).get_page(request.GET.get('page')),
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        # Agar ye error screen par dikhe, toh samajh lo koi purani file cache mein hai
        return HttpResponse(f"Error fixed loading... Please refresh. Details: {str(e)}", status=200)

# --- 2. NEWS DETAIL ---
def news_detail(request, url_city, slug): 
    news = get_object_or_404(News, slug=slug, url_city=url_city)
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", news.youtube_url)
        v_id = match.group(1) if match else None
        
    context = {
        "news": news, 
        "related_news": News.objects.filter(category=news.category).exclude(id=news.id).order_by("-date")[:6],
        "v_id": v_id,
        "meta_description": strip_tags(news.content)[:160] if news.content else news.title,
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT/CATEGORY VIEW ---
def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    if not news_list.exists():
        news_list = News.objects.filter(category__iexact=district).order_by("-date")
        
    page_obj = Paginator(news_list, 15).get_page(request.GET.get('page'))
    return render(request, "mynews/district_news.html", {"district": district, "page_obj": page_obj, **get_common_sidebar_data()})

# --- SEO & LEGAL ---
def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        full_url = f"{SITE_URL.rstrip('/')}/{n.url_city}/{n.slug}/"
        xml += f'  <url><loc>{full_url}</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request): return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")
def ads_txt(request): return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
