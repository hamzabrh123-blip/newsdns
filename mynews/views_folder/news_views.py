from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils.html import strip_tags
from mynews.config import SITE_NAME

# --- 1. HOME VIEW ---
def home(request):
    from mynews.models import News
    from mynews.utils import get_common_sidebar_data
    try:
        query = request.GET.get("q")
        if query:
            news_list = News.objects.filter(title__icontains=query).order_by("-date")
        else:
            news_list = News.objects.filter(is_important=True).order_by("-date")
            
        page_obj = Paginator(news_list, 60).get_page(request.GET.get("page"))
        context = {"page_obj": page_obj}
        context.update(get_common_sidebar_data())
        return render(request, "mynews/home.html", context)
    except Exception as e:
        return HttpResponse(f"Home Page Loading Error: {e}", status=500)

# --- 2. NEWS DETAIL (FB IMAGE FIX KE SAATH) ---
def news_detail(request, url_city, slug):
    from mynews.models import News
    from mynews.utils import get_common_sidebar_data, extract_video_id
    try:
        news = get_object_or_404(News, slug=slug, url_city=url_city)
        related_news = News.objects.filter(district=news.district).exclude(id=news.id).order_by("-date")[:3]
        
        # Absolute URL for Image (FB ko poora link chahiye hota hai)
        if news.image_url:
            og_image = news.image_url
        elif news.image:
            og_image = request.build_absolute_uri(news.image.url)
        else:
            og_image = request.build_absolute_uri('/static/logo.png')

        context = {
            "news": news, 
            "related_news": related_news, 
            "v_id": extract_video_id(news.youtube_url),
            "meta_description": strip_tags(news.content)[:160], 
            "og_title": f"{news.title} | {SITE_NAME}",
            "og_image": og_image, # Ye Facebook ke liye hai
            "meta_url": request.build_absolute_uri(),
        }
        context.update(get_common_sidebar_data())
        return render(request, "mynews/news_detail.html", context)
    except Exception as e:
        print(f"Detail Error: {e}")
        return redirect('home')

# --- 3. MARKET NEWS ---
def market_news_view(request):
    from mynews.models import News
    from mynews.utils import get_common_sidebar_data
    news_list = News.objects.filter(category="Market").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"page_obj": page_obj, "category_name": "बाज़ार न्यूज़"}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/market_news.html", context)

# --- 4. NATIONAL NEWS ---
def national_news(request):
    from mynews.models import News
    from mynews.utils import get_common_sidebar_data
    news_list = News.objects.filter(category="National").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"category": "National", "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/home.html", context)

# --- 5. INTERNATIONAL NEWS ---
def international_news(request):
    from mynews.models import News
    from mynews.utils import get_common_sidebar_data
    news_list = News.objects.filter(category="International").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"category": "International", "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/home.html", context)

# --- 6. TECHNOLOGY NEWS ---
def technology(request):
    from mynews.models import News
    from mynews.utils import get_common_sidebar_data
    news_list = News.objects.filter(category="Technology").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"category": "Technology", "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/home.html", context)

# --- 7. BOLLYWOOD NEWS ---
def bollywood(request):
    from mynews.models import News
    from mynews.utils import get_common_sidebar_data
    news_list = News.objects.filter(category="Bollywood").order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"category": "Bollywood", "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/home.html", context)

# --- 8. DISTRICT NEWS ---
def district_news(request, district):
    from mynews.models import News
    from mynews.utils import get_common_sidebar_data
    news_list = News.objects.filter(district__iexact=district).order_by("-date")
    page_obj = Paginator(news_list, 20).get_page(request.GET.get("page"))
    context = {"district": district, "page_obj": page_obj}
    context.update(get_common_sidebar_data())
    return render(request, "mynews/home.html", context)
