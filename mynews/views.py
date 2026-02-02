import re
import requests
import os
import logging
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

# ✅ WebP to JPG Converter (Facebook/SEO ke liye)
def fix_webp_image(request):
    img_url = request.GET.get('url')
    if not img_url:
        return HttpResponse("No Image URL", status=400)
    try:
        response = requests.get(img_url, timeout=10)
        img = Image.open(BytesIO(response.content))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return HttpResponse(buffer.getvalue(), content_type="image/jpeg")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

# --- FB AUTO POST FUNCTION ---
def post_to_facebook_network(news_obj):
    access_token = os.environ.get('FB_ACCESS_TOKEN')
    page_id = os.environ.get('FB_PAGE_ID')
    group1_id = os.environ.get('FB_GROUP_1_ID')
    group2_id = os.environ.get('FB_GROUP_2_ID')
    
    if not access_token:
        print("❌ DEBUG: FB_ACCESS_TOKEN not found in Render settings!")
        return 

    # .html suffix ke sath URL
    url_city = news_obj.url_city if news_obj.url_city else "news"
    news_url = f"{SITE_URL}/{url_city}/{news_obj.slug}.html"
    
    destinations = [page_id, group1_id, group2_id]
    
    for target in destinations:
        if target:
            fb_url = f"https://graph.facebook.com/v19.0/{target}/feed"
            payload = {
                'message': f"🔥 {news_obj.title}\n\nपूरी खबर यहाँ पढ़ें 👇",
                'link': news_url,
                'access_token': access_token
            }
            try:
                response = requests.post(fb_url, data=payload, timeout=10)
                res_data = response.json()
                if response.status_code == 200:
                    # Sirf update flag, save dubara nahi (taaki loop na bane)
                    News.objects.filter(id=news_obj.id).update(is_fb_posted=True)
                    print(f"✅ FB Success for {target}")
                else:
                    print(f"❌ FB API Error for {target}: {res_data}")
            except Exception as e:
                print(f"❌ FB Post Connection Error for {target}: {str(e)}")

# --- Video ID extractor ---
def extract_video_id(url):
    if not url: return None
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

# --- Sidebar Data ---
def get_common_sidebar_data():
    return {
        "bazaar_sidebar": News.objects.filter(category="Market").order_by("-date")[:5],
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:10],
        "technology_sidebar": News.objects.filter(category="Technology").order_by("-date")[:3],
        "bollywood_sidebar": News.objects.filter(category="Bollywood").order_by("-date")[:3],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
    }

def home(request):
    try:
        query = request.GET.get("q")
        news_list = News.objects.filter(title__icontains=query).order_by("-date") if query else News.objects.filter(is_important=True).order_by("-date")
        page_obj = Paginator(news_list, 60).get_page(request.GET.get("page"))
        context = {
            "page_obj": page_obj,
            "meta_description": "Uttar World News: Get the latest breaking news from Uttar Pradesh, India, and around the world.",
            "meta_keywords": "Uttar World, UttarWorld News, Latest UP News, Breaking News India",
        }
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except: return HttpResponse("Home Page Loading Error", status=500)

def news_detail(request, url_city, slug): 
    try:
        news = get_object_or_404(News, slug=slug, url_city=url_city)
        related_news = News.objects.filter(district=news.district).exclude(id=news.id).order_by("-date")[:3]
        v_id = extract_video_id(news.youtube_url)
        
        # Admin wale keywords dynamic karein
        keywords = news.meta_keywords if news.meta_keywords else "Uttar World, UttarWorld News, Latest UP News"

        # FB Posting trigger (Sirf pehli baar)
        if not news.is_fb_posted:
            post_to_facebook_network(news)

        context = {
            "news": news, 
            "related_news": related_news,
            "meta_description": strip_tags(news.content)[:160],
            "meta_keywords": keywords,
            "og_title": f"{news.title} | {SITE_NAME}",
            "v_id": v_id, 
        }
        context.update(get_common_sidebar_data())
        return render(request, "mynews/news_detail.html", context)
    except: return redirect('home')

# --- Category Views ---
def market_news_view(request):
    try:
        news_list = News.objects.filter(category="Market").order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"page_obj": page_obj, "category_name": "बाज़ार न्यूज़"}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/market_news.html", context)
    except: return redirect('home')

def national_news(request):
    try:
        news_list = News.objects.filter(category="National").order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"category": "National", "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except: return redirect('home')

def international_news(request):
    try:
        news_list = News.objects.filter(category="International").order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"category": "International", "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except: return redirect('home')

def technology(request):
    try:
        news_list = News.objects.filter(category="Technology").order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"category": "Technology", "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except: return redirect('home')

def bollywood(request):
    try:
        news_list = News.objects.filter(category="Bollywood").order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"category": "Bollywood", "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except: return redirect('home')

def district_news(request, district):
    try:
        news_list = News.objects.filter(district__iexact=district).order_by("-date")
        page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
        context = {"district": district, "page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except: return redirect('home')

def contact_us(request):
    success = False
    if request.method == "POST":
        try:
            send_mail(f"Contact", request.POST.get('message'), settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
            success = True
        except: pass
    context = {"success": success}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/contact_us.html", context)

def privacy_policy(request): return render(request, "mynews/privacy_policy.html")
def about_us(request): return render(request, "mynews/about_us.html")
def disclaimer(request): return render(request, "mynews/disclaimer.html")

def ads_txt(request): 
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def robots_txt(request):
    content = f"User-Agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {SITE_URL}/sitemap.xml"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += f"  <url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>\n"
    xml += f"  <url><loc>{SITE_URL}/market-news/</loc><priority>0.9</priority></url>\n"
    for n in items:
        city = n.url_city if n.url_city else "news"
        xml += f"  <url>\n    <loc>{SITE_URL}/{city}/{n.slug}.html</loc>\n    <lastmod>{n.date.strftime('%Y-%m-%d')}</lastmod>\n  </url>\n"
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")
