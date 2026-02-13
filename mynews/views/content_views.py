import re
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from ..models import News
from .base import get_common_sidebar_data, published_news

SITE_URL = "https://uttarworld.com"

# --- NEWS DETAIL VIEW ---
def news_detail(request, url_city, slug):
    # iexact aur strip se slug ki matching solid ho jati hai
    news = get_object_or_404(News, slug__iexact=slug.strip(), status__iexact="Published")
    
    v_id = None
    if news.youtube_url:
        # YouTube ID nikalne ka mast regex
        match = re.search(r"(?:v=|youtu\.be/|shorts/|embed/|live/|^)([a-zA-Z0-9_-]{11})", news.youtube_url)
        v_id = match.group(1) if match else None

    return render(request, "mynews/news_detail.html", {
        "news": news,
        "v_id": v_id,
        "related_news": published_news().filter(category=news.category).exclude(id=news.id)[:6],
        **get_common_sidebar_data()
    })

# --- FB API VIEW ---
def fb_news_api(request):
    # News list uthayi aur JSON format mein bhej di
    news_list = published_news()[:20]
    data = []
    for n in news_list:
        city = (n.url_city or "news").strip()
        slug = n.slug.strip()
        data.append({
            "id": n.id,
            "title": n.title,
            # SITE_URL.rstrip se double slash ka khatra khatam
            "url": f"{SITE_URL.rstrip('/')}/{city}/{slug}/"
        })
    return JsonResponse(data, safe=False)
