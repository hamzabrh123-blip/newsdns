import re, requests, os, logging, facebook
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from .models import News
from django.conf import settings
from django.utils.html import strip_tags
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

SITE_URL = "https://uttarworld.com"
SITE_NAME = "Uttar World News"
# --- FB AUTO POST FUNCTION (Final Fix) ---
def post_to_facebook_network(news_obj):
    # Render ke Config Vars se data uthana
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_id = os.environ.get('FB_PAGE_ID')
    group1_id = os.environ.get('FB_GROUP_1_ID')
    group2_id = os.environ.get('FB_GROUP_2_ID')
    
    if not access_token:
        print("❌ FB Error: FB_ACCESS_TOKEN missing!")
        return False

    # --- URL FIX (MATCHING YOUR URLS.PY) ---
    # Tumhare urls.py ke hisab se yahan .html hona chahiye
    url_city = news_obj.url_city if news_obj.url_city else "news"
    news_url = f"{SITE_URL}/{url_city}/{news_obj.slug}.html"
    
    # Image logic: ImgBB ya Cloudinary link
    image_to_share = news_obj.image_url if news_obj.image_url else ""
    
    destinations = [d for d in [page_id, group1_id, group2_id] if d]
    success_all = True

    for target in destinations:
        # Facebook Graph API call
        fb_api_url = f"https://graph.facebook.com/v19.0/{target}/feed"
        payload = {
            'message': f"🔥 {news_obj.title}\n\nपूरी खबर यहाँ पढ़ें 👇",
            'link': news_url,
            'picture': image_to_share,
            'access_token': access_token
        }
        
        try:
            # Facebook ko requests bhej rahe hain
            response = requests.post(fb_api_url, data=payload, timeout=15)
            res_data = response.json()
            
            if response.status_code == 200:
                print(f"✅ FB Success for {target}: ID {res_data.get('id')}")
            else:
                success_all = False
                # Error message Render logs mein dikhega
                print(f"❌ FB API Error ({target}): {res_data.get('error', {}).get('message')}")
        except Exception as e:
            success_all = False
            print(f"❌ FB Connection Failed for {target}: {str(e)}")
    
    return success_all

# --- Home Page & Detail Views ---
def home(request):
    try:
        query = request.GET.get("q")
        news_list = News.objects.filter(title__icontains=query).order_by("-date") if query else News.objects.filter(is_important=True).order_by("-date")
        page_obj = Paginator(news_list, 60).get_page(request.GET.get("page"))
        context = {
            "page_obj": page_obj,
            "meta_description": "Uttar World News: Latest breaking news from UP, India.",
            "meta_keywords": "Uttar World, UttarWorld News, Latest UP News",
        }
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except Exception as e: 
        logger.error(f"Home Error: {e}")
        return HttpResponse("Home Page Error", status=500)

def news_detail(request, url_city, slug): 
    news = get_object_or_404(News, slug=slug, url_city=url_city)
    related_news = News.objects.filter(district=news.district).exclude(id=news.id).order_by("-date")[:3]
    
    # YouTube ID Extraction
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", news.youtube_url)
        v_id = match.group(1) if match else None

    context = {
        "news": news, 
        "related_news": related_news,
        "meta_description": strip_tags(news.content)[:160],
        "og_title": f"{news.title} | {SITE_NAME}",
        "v_id": v_id, 
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/news_detail.html", context)

# --- Sidebar & Static Views (Shortened for brevity) ---
def get_common_sidebar_data():
    return {
        "bazaar_sidebar": News.objects.filter(category="Market").order_by("-date")[:5],
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
    }

# Baki saare views (robots, sitemap, category) as-is rahenge
def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        city = n.url_city or "news"
        xml += f"  <url><loc>{SITE_URL}/{city}/{n.slug}/</loc><lastmod>{n.date.strftime('%Y-%m-%d')}</lastmod></url>\n"
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")
