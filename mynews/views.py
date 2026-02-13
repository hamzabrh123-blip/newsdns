import re
import logging
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from .models import News
from .constants import LOCATION_DATA

logger = logging.getLogger(__name__)
SITE_URL = "https://uttarworld.com"

# ---------------------------------------------------
# HELPER: Published News Only
# ---------------------------------------------------
def published_news():
    return News.objects.filter(status__iexact="Published").order_by("-date")

# ---------------------------------------------------
# 1. FB API
# ---------------------------------------------------
def fb_news_api(request):
    try:
        news_list = published_news()[:20]
        data = []
        for n in news_list:
            city = (n.url_city or "news").strip()
            data.append({
                "id": n.id,
                "title": n.title,
                "url": f"{SITE_URL.rstrip('/')}/{city}/{n.slug.strip()}/"
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(f"FB API Error: {e}")
        return JsonResponse({"error": "Server Error"}, status=500)

# ---------------------------------------------------
# 2. SIDEBAR DATA
# ---------------------------------------------------
def get_common_sidebar_data():
    published = published_news()
    
    # 1. UP SIDEBAR: Jo UP category ya kisi bhi District se juda ho
    up_sidebar = published.filter(
        Q(category__icontains="uttar") | 
        Q(category__icontains="up") | 
        Q(district__isnull=False)
    ).exclude(category__icontains="national").exclude(category__icontains="international")[:8]

    # 2. WORLD SIDEBAR: International news
    world_sidebar = published.filter(
        Q(category__icontains="international") | 
        Q(category__icontains="world") | 
        Q(category__icontains="duniya")
    )[:5]

    # 3. BAZAAR SIDEBAR: Market/Business
    bazaar_sidebar = published.filter(
        Q(category__icontains="market") | 
        Q(category__icontains="bazaar") | 
        Q(category__icontains="business")
    )[:5]

    # 4. SPORTS SIDEBAR: Khel
    sports_sidebar = published.filter(
        Q(category__icontains="sports") | 
        Q(category__icontains="khel")
    )[:5]

    # --- DYNAMIC CITIES LOGIC ---
    exclude_keys = ["National", "International", "Sports", "Bollywood", "Hollywood", "Technology", "Market", "Entertainment"]
    used_districts = published.values_list("district", flat=True).distinct()

    dynamic_cities = []
    for eng, hin, cat_slug in LOCATION_DATA:
        # Agar district use hua hai aur wo main categories mein nahi hai
        if eng in used_districts and eng not in exclude_keys:
            dynamic_cities.append({"id": eng.strip(), "name": hin})

    return {
        "up_sidebar": up_sidebar,
        "world_sidebar": world_sidebar,
        "bazaar_sidebar": bazaar_sidebar,
        "sports_sidebar": sports_sidebar,
        "dynamic_up_cities": dynamic_cities,
        "dynamic_big_categories": [
            {"id": "National", "name": "देश"},
            {"id": "International", "name": "दुनिया"},
            {"id": "Sports", "name": "खेल"},
            {"id": "Market", "name": "बाज़ार"},
        ],
    }

# ---------------------------------------------------
# 3. HOME PAGE
# ---------------------------------------------------
def home(request):
    try:
        common_data = get_common_sidebar_data()
        all_news = News.objects.filter(status__iexact="Published").order_by("-date")

        page_number = request.GET.get("page", 1)
        paginator = Paginator(all_news, 12)
        other_news_page = paginator.get_page(page_number)

        context = {
            "other_news": other_news_page,
            "page_number": int(page_number),
            **common_data
        }

        if str(page_number) == "1":
            # 1. TOP HIGHLIGHTS (Wahi 12 News)
            highlights = all_news.filter(show_in_highlights=True)[:12]
            if not highlights.exists():
                highlights = all_news[:12]

            # 2. BHARAT (National) - Sirf Desh ki khabrein
            # 'nation' keyword se National, Rashtriya sab cover hoga
            national = all_news.filter(
                Q(category__icontains="national") | Q(category__icontains="bharat") | Q(category__icontains="india")
            )[:4]
            
            # 3. DUNIYA (World) - Sirf Videsh ki khabrein
            world = all_news.filter(
                Q(category__icontains="international") | Q(category__icontains="world") | Q(category__icontains="videsh")
            )[:4]

            # 4. UP NEWS (Regional)
            # Yahan humne National aur World ko STRICTLY nikaal diya hai
            # Taaki Varanasi/Lucknow ki news National mein na ghuse
            up_news_list = all_news.filter(
                Q(category__icontains="up") | 
                Q(category__icontains="uttar") | 
                Q(district__isnull=False)
            ).exclude(
                Q(category__icontains="up") | Q(category__icontains="up") | Q(category__icontains="up")
            )[:12]

            context.update({
                "top_5_highlights": highlights,
                "national_news": national,
                "world_news": world,
                "up_news": up_news_list,
                "entertainment_news": all_news.filter(Q(category__icontains="bollywood") | Q(category__icontains="manoranjan"))[:6],
            })

        return render(request, "mynews/home.html", context)
    except Exception as e:
        logger.error(f"Home Error: {e}")
        return HttpResponse("Updating Sections...")
# ---------------------------------------------------
# 4. NEWS DETAIL
# ---------------------------------------------------
def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug__iexact=slug.strip(), status__iexact="Published")
    
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|youtu\.be/|shorts/|embed/|live/|^)([a-zA-Z0-9_-]{11})", news.youtube_url)
        if match:
            v_id = match.group(1)

    context = {
        "news": news,
        "v_id": v_id,
        "related_news": published_news().filter(category__iexact=news.category).exclude(id=news.id)[:6],
        **get_common_sidebar_data()
    }
    return render(request, "mynews/news_detail.html", context)

# ---------------------------------------------------
# 5. DISTRICT / CATEGORY PAGE
# ---------------------------------------------------
def district_news(request, district):
    dist_name = district.strip()
    news_list = published_news().filter(
        Q(district__iexact=dist_name) | Q(category__iexact=dist_name) | Q(url_city__iexact=dist_name)
    )
    
    page_obj = Paginator(news_list, 15).get_page(request.GET.get("page"))

    return render(request, "mynews/district_news.html", {
        "district": dist_name,
        "page_obj": page_obj,
        "news_count": news_list.count(),
        **get_common_sidebar_data()
    })

# ---------------------------------------------------
# 6. SEO & LEGAL
# ---------------------------------------------------
def sitemap_xml(request):
    items = published_news()[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for n in items:
        city = (n.url_city or "news").strip()
        xml += f'<url><loc>{SITE_URL}/{city}/{n.slug.strip()}/</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>'
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request):
    return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml", content_type="text/plain")

def ads_txt(request):
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
def contact_us(request): return render(request, "mynews/contact_us.html", get_common_sidebar_data())
def disclaimer(request): return render(request, "mynews/disclaimer.html", get_common_sidebar_data())
