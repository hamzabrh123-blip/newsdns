import re, logging, html, requests
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News
from django.utils.html import strip_tags
from django.db.models import Case, When, Value, IntegerField

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"

# --- SIDEBAR LOGIC ---
def get_common_sidebar_data():
    return {
        "bazaar_sidebar": News.objects.filter(district="Market").order_by("-date")[:5],
        "bharat_sidebar": News.objects.filter(district="UP-National").order_by("-date")[:5],
        "up_sidebar": News.objects.exclude(district__in=["Market", "Sports", "UP-National"]).exclude(district__startswith="Int-").order_by("-date")[:10],
        "world_sidebar": News.objects.filter(district__startswith="Int-").order_by("-date")[:5],
        "sports_sidebar": News.objects.filter(district="Sports").order_by("-date")[:5],
    }

# --- 1. HOME PAGE (With Sections & Pagination) ---
def home(request):
    try:
        query = request.GET.get("q")
        if query:
            news_list = News.objects.filter(title__icontains=query).order_by("-date")
            page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
            return render(request, "mynews/home.html", {"page_obj": page_obj, **get_common_sidebar_data()})
        
        # Priority Logic
        all_important = News.objects.filter(is_important=True).annotate(
            priority=Case(
                When(district__startswith="Int-", then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        ).order_by("priority", "-date")
        
        # Sections for Home
        up_news = News.objects.exclude(district__in=["Market", "Sports", "UP-National"]).exclude(district__startswith="Int-").order_by("-date")
        national_news = News.objects.filter(district="UP-National").order_by("-date")
        world_news = News.objects.filter(district__startswith="Int-").order_by("-date")
        
        # PAGINATION logic for "Other News" section
        paginator = Paginator(all_important[5:], 10) # Pehli 5 grid mein, baaki paginated
        page_number = request.GET.get('page')
        other_news_page = paginator.get_page(page_number)
        
        context = {
            "top_5_highlights": all_important[:5],
            "up_news": up_news[:4],
            "national_news": national_news[:3],
            "world_news": world_news[:3],
            "other_news": other_news_page, # Ye template mein pager chalayega
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
            **get_common_sidebar_data()
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse("Home Page Error", status=500)

# --- 2. NEWS DETAIL ---
def news_detail(request, url_city, slug): 
    news = get_object_of_404(News, slug=slug, url_city=url_city)
    related_news = News.objects.filter(district=news.district).exclude(id=news.id).order_by("-date")[:6]
    
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", news.youtube_url)
        v_id = match.group(1) if match else None
        
    context = {
        "news": news, 
        "related_news": related_news, 
        "v_id": v_id,
        "meta_description": strip_tags(news.content)[:160] if news.content else news.title,
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT VIEW ---
def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    page_obj = Paginator(news_list, 15).get_page(request.GET.get('page'))
    
    context = {
        "district": district, 
        "page_obj": page_obj,
        **get_common_sidebar_data()
    }
    return render(request, "mynews/district_news.html", context)

# --- 4. SEO & STATIC ---
def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        xml += f'  <url><loc>{SITE_URL.rstrip("/")}{n.get_absolute_url()}</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request): 
    return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")

def ads_txt(request): 
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
