import re, logging, html
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"

# --- SIDEBAR LOGIC (Sabhi pages ke liye) ---
def get_common_sidebar_data():
    return {
        # Market sidebar
        "bazaar_sidebar": News.objects.filter(district="Market").order_by("-date")[:5],
        # National News
        "bharat_sidebar": News.objects.filter(district="UP-National").order_by("-date")[:10],
        # International / Middle East News
        "world_sidebar": News.objects.filter(district__startswith="Int-").order_by("-date")[:5],
        # Sports News
        "sports_sidebar": News.objects.filter(district="Sports").order_by("-date")[:5],
    }

# --- 1. HOME PAGE ---
def home(request):
    try:
        query = request.GET.get("q")
        if query:
            news_list = News.objects.filter(title__icontains=query).order_by("-date")
            page_obj = Paginator(news_list, 40).get_page(request.GET.get("page"))
            return render(request, "mynews/home.html", {"page_obj": page_obj, **get_common_sidebar_data()})
        
        all_important = News.objects.filter(is_important=True).order_by("-date")
        
        # Top 3 Highlights
        top_3_highlights = all_important[:3]
        for n in top_3_highlights:
            clean = strip_tags(n.content)
            n.clean_home_text = html.unescape(clean).replace('\xa0', ' ').strip()[:300] + "..."

        # Baki Cards
        other_news = all_important[3:43]

        context = {
            "top_3_highlights": top_3_highlights,
            "other_news": other_news,
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
        }
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)

    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse("Home Page Error", status=500)

# --- 2. NEWS DETAIL ---
def news_detail(request, url_city, slug): 
    news = get_object_or_404(News, slug=slug, url_city=url_city)
    # Related news usi district/zone ki dikhayenge
    related_news = News.objects.filter(district=news.district).exclude(id=news.id).order_by("-date")[:3]
    
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", news.youtube_url)
        v_id = match.group(1) if match else None
        
    context = {"news": news, "related_news": related_news, "v_id": v_id}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/news_detail.html", context)

# --- 3. UNIVERSAL DISTRICT/ZONE VIEW (The Big Controller) ---
def district_news(request, district):
    # district parameter mein 'Int-MiddleEast', 'Sports', 'Lucknow-UP' kuch bhi aa sakta hai
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    
    # Pagination
    paginator = Paginator(news_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "district": district, 
        "page_obj": page_obj,
        **get_common_sidebar_data()
    }
    # Hum aapka wahi sundar district_news.html use karenge
    return render(request, "mynews/district_news.html", context)

# --- 4. SEO & STATIC ---
def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        city = n.url_city or "news"
        xml += f'  <url><loc>{SITE_URL}/{city}/{n.slug}</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request): return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml", content_type="text/plain")
def ads_txt(request): return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
def privacy_policy(request): return render(request, "mynews/privacy_policy.html")
def about_us(request): return render(request, "mynews/about_us.html")
def contact_us(request): return render(request, "mynews/contact_us.html")
def disclaimer(request): return render(request, "mynews/disclaimer.html")
