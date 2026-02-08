import re, logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse # JsonResponse joda gaya hai
from .models import News
from django.utils.html import strip_tags
from django.db.models import Q

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"

# --- 0. UPDATED: API FOR BULK PC SCRIPT ---
def fb_news_api(request):
    """
    Ye function Admin ke tick ka wait nahi karega.
    Seedha latest 20 Published news phenk dega.
    """
    # Filter hataya (is_fb_posted wala) taaki Bulk mein sab utha sake
    news_list = News.objects.filter(status='Published').order_by('-date')[:20]
    
    data = []
    for n in news_list:
        # City handling (agar null ho toh 'news' use karega)
        city = n.url_city if n.url_city else 'news'
        data.append({
            'id': n.id,
            'title': n.title,
            'url': f"{SITE_URL.rstrip('/')}/{city}/{n.slug}/"
        })
    return JsonResponse(data, safe=False)

# --- Common Data Function ---
def get_common_sidebar_data():
    used_districts = News.objects.exclude(district__isnull=True).values_list('district', flat=True).distinct()
    dynamic_cities = []
    for eng, hin, cat in News.LOCATION_DATA:
        if eng in used_districts:
            dynamic_cities.append({'id': eng, 'name': hin})
    
    return {
        "up_sidebar": News.objects.filter(category__icontains="UP").order_by("-date")[:10],
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:5],
        "world_sidebar": News.objects.filter(category="International").order_by("-date")[:5],
        "bazaar_sidebar": News.objects.filter(category="Market").order_by("-date")[:5],
        "sports_sidebar": News.objects.filter(category="Sports").order_by("-date")[:5],
        "dynamic_up_cities": dynamic_cities,
    }

# --- 1. HOME PAGE ---
def home(request):
    try:
        common_data = get_common_sidebar_data()
        query = request.GET.get("q")

        if query:
            news_list = News.objects.filter(title__icontains=query).order_by("-date")
            page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
            return render(request, "mynews/home.html", {"page_obj": page_obj, **common_data})
        
        # --- TOP HEADLINES FIXED (Model Field: show_in_highlights) ---
        # Ab ye is_important (Breaking) se nahi, show_in_highlights (Tick) se chalega
        top_highlights = News.objects.filter(show_in_highlights=True).order_by("-date")[:5]
        
        context = {
            "top_5_highlights": top_highlights, # Admin panel se tick wali news aayengi
            "up_news": News.objects.filter(category__icontains="UP").order_by("-date")[:4],
            "national_news": News.objects.filter(category="National").order_by("-date")[:4],
            "world_news": News.objects.filter(category="International").order_by("-date")[:4],
            "sports_news": News.objects.filter(category="Sports").order_by("-date")[:4],
            
            # --- Ye do naye sections tere template ke liye ---
            "bollywood_news": News.objects.filter(district="Bollywood").order_by("-date")[:4],
            "technology_news": News.objects.filter(district="Technology").order_by("-date")[:4],
            
            "other_news": Paginator(News.objects.all().order_by("-date"), 10).get_page(request.GET.get('page')),
            "meta_description": "Uttar World News: Latest breaking news from UP, India and World.",
            **common_data
        }
        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse(f"System Check: {str(e)}", status=200)
        
# --- 2. NEWS DETAIL ---
def news_detail(request, url_city, slug): 
    news = get_object_or_404(News, slug=slug)
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", news.youtube_url)
        v_id = match.group(1) if match else None
        
    context = {
        "news": news, 
        "og_title": news.title,
        "related_news": News.objects.filter(category=news.category).exclude(id=news.id).order_by("-date")[:6],
        "v_id": v_id,
        "meta_description": strip_tags(news.content)[:160] if news.content else news.title,
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# --- 3. DISTRICT/CATEGORY VIEW ---
def district_news(request, district):
    try:
        # Ab ye district, category aur url_city teeno mein dhoondega
        # Isse 'technology' wala masla 100% solve ho jayega
        news_list = News.objects.filter(
            Q(district__iexact=district) | 
            Q(category__icontains=district) | 
            Q(url_city__iexact=district)
        ).order_by("-date")
        
        paginator = Paginator(news_list, 15)
        page_obj = paginator.get_page(request.GET.get('page'))

        context = {
            "district": district, 
            "page_obj": page_obj, 
            "news_count": news_list.count(),
            **get_common_sidebar_data()
        }
        return render(request, "mynews/district_news.html", context)
    except Exception as e:
        logger.error(f"View Error for {district}: {e}")
        return render(request, "mynews/district_news.html", {
            "district": district,
            "error_msg": "Abhi koi news uplabdth nahi hai.",
            **get_common_sidebar_data()
        })

# --- 4. SEO & LEGAL ---
def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        city = n.url_city if n.url_city else 'news'
        full_url = f"{SITE_URL.rstrip('/')}/{city}/{n.slug}/"
        xml += f'  <url><loc>{full_url}</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>\n'
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request): return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL.rstrip('/')}/sitemap.xml", content_type="text/plain")
def ads_txt(request): return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
