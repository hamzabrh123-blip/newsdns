import re
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from ..models import News
from .base import get_common_sidebar_data, published_news

SITE_URL = "https://uttarworld.com"

def news_detail(request, url_city, slug):
    news = get_object_or_404(News, slug__iexact=slug.strip(), status__iexact="Published")
    v_id = None
    if news.youtube_url:
        match = re.search(r"(?:v=|youtu\.be/|shorts/|embed/|live/|^)([a-zA-Z0-9_-]{11})", news.youtube_url)
        v_id = match.group(1) if match else None

    return render(request, "mynews/news_detail.html", {
        "news": news,
        "v_id": v_id,
        "related_news": published_news().filter(category=news.category).exclude(id=news.id)[:6],
        **get_common_sidebar_data()
    })

def fb_news_api(request):
    data = [{"id": n.id, "title": n.title, "url": f"{SITE_URL}/{n.url_city or 'news'}/{n.slug}/"} for n in published_news()[:20]]
    return JsonResponse(data, safe=False)
