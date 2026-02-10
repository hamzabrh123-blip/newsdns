from .models import News
from .constants import LOCATION_DATA   # ✅ यही missing था

def site_visits(request):
    return {'site_visits': 0}

def news_data_processor(request):
    # ब्रेकिंग न्यूज़
    breaking_news = News.objects.filter(
        is_important=True,
        status='Published'
    ).order_by('-date')[:20]

    # जिन जिलों की न्यूज़ मौजूद है
    active_districts = set(
        News.objects.exclude(district__isnull=True)
        .values_list('district', flat=True)
        .distinct()
    )

    dynamic_up_cities = []

    # ✅ अब News.LOCATION_DATA नहीं, सीधे LOCATION_DATA
    for eng, hin, city_slug in LOCATION_DATA:
        if eng in active_districts:
            dynamic_up_cities.append({
                'id': eng,
                'name': hin,
                'slug': city_slug
            })

    return {
        'important_news': breaking_news,
        'dynamic_up_cities': dynamic_up_cities,
    }
