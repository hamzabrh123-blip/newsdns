from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.db import models
from django.core.paginator import Paginator
from django.http import HttpResponse
from .models import News, Comment
from django.conf import settings
import logging

# Logger setup
logger = logging.getLogger(__name__)

# ✅ OPTIMIZED SIDEBAR DATA
def get_common_sidebar_data():
    return {
        "bharat_sidebar": News.objects.filter(category="National").order_by("-date")[:10],
        "duniya_sidebar": News.objects.filter(category="International").order_by("-date")[:10],
        "technology_sidebar": News.objects.filter(category="Technology").order_by("-date")[:3],
        "bollywood_sidebar": News.objects.filter(category="Bollywood").order_by("-date")[:3],
        "lucknow_up_sidebar": News.objects.filter(district='Lucknow-UP').order_by("-date")[:10],
        "up_national_sidebar": News.objects.filter(district='UP-National').order_by("-date")[:3],
        "purvanchal_sidebar": News.objects.filter(district='Purvanchal').order_by("-date")[:5],
        "bahraich_gonda_sidebar": News.objects.filter(district='Bahraich-Gonda').order_by("-date")[:10],
        "balrampur_shravasti_sidebar": News.objects.filter(district='Balrampur-Shravasti').order_by("-date")[:3],
        "sitapur_barabanki_sidebar": News.objects.filter(district='Sitapur-Barabanki').order_by("-date")[:5],
    }

# ================= HOME (SEO FIXED) =================
def home(request):
    query = request.GET.get("q")
    if query:
        news_list = News.objects.filter(title__icontains=query).order_by("-date")
    else:
        news_list = News.objects.filter(is_important=True).order_by("-date")

    paginator = Paginator(news_list, 20) 
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "meta_description": "UP Halchal News: Latest Uttar Pradesh News in Hindi, Breaking News, Politics, Railway, and Education updates. उत्तर प्रदेश की हर हलचल पर हमारी नज़र। पढ़ें देश-दुनिया की ताज़ा खबरें।",
        "meta_keywords": "UP Halchal, UP News Hindi, Latest News, Breaking News, Uttar Pradesh News Portal, UP Khabar, Hindi News, Politics News UP, Railway News Hindi",
        "og_title": "UP Halchal News | सबसे तेज़, सबसे सटीक न्यूज़ पोर्टल",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/home.html", context)

# ================= NEWS DETAIL (DYNAMIC SEO FIXED) =================
def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    comments = Comment.objects.filter(news=news).order_by("-date")

    if news.youtube_url:
        if "watch?v=" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace("watch?v=", "embed/")
        elif "youtu.be/" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace("youtu.be/", "www.youtube.com/embed/")

    context = {
        "news": news,
        "comments": comments,
        "meta_description": f"{news.title}. Get the latest updates on {news.category} and {news.district} news in Hindi on UP Halchal. उत्तर प्रदेश और देश की बड़ी खबरें।",
        "meta_keywords": f"{news.category} News, {news.district} Khabar, UP News Today, {news.title[:50]}, UP Halchal Updates",
        "og_title": f"{news.title} - UP Halchal",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/news_detail.html", context)

# ================= DISTRICT NEWS (DYNAMIC SEO) =================
def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    paginator = Paginator(news_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "district": district, 
        "page_obj": page_obj,
        "meta_description": f"Latest {district} News in Hindi. Get local breaking news, politics, and daily updates from {district}, Uttar Pradesh on UP Halchal.",
        "meta_keywords": f"{district} News, {district} Hindi Khabar, {district} Local Updates, UP Halchal {district}, News from {district}",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

# ================= NATIONAL NEWS =================
def national_news(request):
    news_list = News.objects.filter(category="National").order_by("-date")
    paginator = Paginator(news_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "district": "भारत (National)",
        "meta_description": "National News in Hindi: Read latest India news, politics, and national updates on UP Halchal. देश की बड़ी खबरें और ताज़ा समाचार।",
        "meta_keywords": "National News Hindi, India News, Politics India, देश की खबरें, भारत समाचार, UP Halchal National",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

# ================= TECHNOLOGY NEWS =================
def technology(request):
    news_list = News.objects.filter(category="Technology").order_by("-date")
    paginator = Paginator(news_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "district": "टेक्नॉलोजी (Technology)",
        "meta_description": "Latest Technology News in Hindi: Mobiles, Gadgets, and Tech updates. गैजेट्स और टेक जगत की हर हलचल हिंदी में सिर्फ UP Halchal पर।",
        "meta_keywords": "Tech News Hindi, Technology Updates, Mobile News Hindi, गैजेट्स समाचार, टेक्नोलॉजी न्यूज़, UP Halchal Tech",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

# ================= BOLLYWOOD NEWS =================
def bollywood(request):
    news_list = News.objects.filter(category="Bollywood").order_by("-date")
    paginator = Paginator(news_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "district": "बॉलीवुड (Bollywood)",
        "meta_description": "Bollywood News in Hindi: Latest Movie Reviews, Celeb Gossip, and Entertainment News. मनोरंजन की दुनिया की ताज़ा खबरें हिंदी में।",
        "meta_keywords": "Bollywood News, Entertainment News Hindi, Movie Reviews, बॉलीवुड समाचार, मनोरंजन न्यूज़, UP Halchal Entertainment",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

# ================= INTERNATIONAL NEWS =================
def international_news(request):
    news_list = News.objects.filter(category="International").order_by("-date")
    paginator = Paginator(news_list, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "district": "दुनिया (International)",
        "meta_description": "International News in Hindi: World News, Global updates, and International affairs. दुनिया भर की बड़ी खबरें हिंदी में पढ़ें।",
        "meta_keywords": "World News Hindi, International News, Global Updates, विदेश समाचार, दुनिया की खबरें, UP Halchal International",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/district_news.html", context)

# ================= CONTACT US =================
def contact_us(request):
    success = False
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message_body = request.POST.get("message")
        subject = f"UP Halchal News: Message from {name}"
        full_message = f"Sender Name: {name}\nSender Email: {email}\n\nMessage:\n{message_body}"
        try:
            send_mail(subject=subject, message=full_message, from_email=settings.EMAIL_HOST_USER, recipient_list=[settings.EMAIL_HOST_USER], fail_silently=False)
            success = True
        except Exception as e:
            logger.error(f"Contact Form Error: {e}")
            success = True 

    context = {
        "success": success,
        "meta_description": "Contact UP Halchal News: Reach out to us for news tips, advertisements, or queries. हमसे संपर्क करें।",
        "meta_keywords": "Contact UP Halchal, News Tips, Advertise with us",
    }
    context.update(get_common_sidebar_data())
    return render(request, "mynews/contact_us.html", context)

# ================= STATIC PAGES (ADSENSE READY) =================
def privacy_policy(request):
    context = {
        "meta_description": "Privacy Policy of UP Halchal News: Learn how we protect your information. हमारी गोपनीयता नीति के बारे में जानें।",
        "meta_keywords": "Privacy Policy, Data Protection, UP Halchal Terms"
    }
    return render(request, "mynews/privacy_policy.html", context)

def about_us(request):
    context = {
        "meta_description": "About UP Halchal News: Your trusted news source from Uttar Pradesh. उत्तर प्रदेश का उभरता हुआ न्यूज़ पोर्टल।",
        "meta_keywords": "About Us, UP Halchal Team, News Portal UP"
    }
    return render(request, "mynews/about_us.html", context)
    
def disclaimer(request):
    context = {
        "meta_description": "Disclaimer for UP Halchal News: Terms and conditions regarding our content. हमारी नियम और शर्तें।",
        "meta_keywords": "Disclaimer, Content Policy, UP Halchal Terms"
    }
    return render(request, "mynews/disclaimer.html", context)

# ================= SEO FILES =================
def ads_txt(request):
    content = "google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")

def robots_txt(request):
    content = "User-Agent: *\nAllow: /\nDisallow: /admin_login.html\nDisallow: /admin_verify.html\nSitemap: https://halchal.onrender.com/sitemap.xml"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    base_url = "https://halchal.onrender.com" 
    news_items = News.objects.exclude(slug__isnull=True).exclude(slug="").order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += f"<url><loc>{base_url}/</loc><priority>1.0</priority></url>"
    for news in news_items:
        url = f"{base_url}/{news.slug}/" 
        xml += f"<url><loc>{url}</loc><priority>0.8</priority></url>"
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")
