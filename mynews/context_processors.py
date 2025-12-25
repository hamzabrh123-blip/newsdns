from .models import News
from django.core.cache import cache

def important_news(request):
    return {
        'important_news': News.objects.filter(
            is_important=True
        ).order_by('-date')[:20]
    }

def site_visits(request):
    visits = cache.get("visits", 0)
    return {"visits": visits}
