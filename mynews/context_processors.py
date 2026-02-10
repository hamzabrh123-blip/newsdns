from .models import News
from .constants import UP_DISTRICTS, BIG_CATEGORIES # Dono ko alag import karo

def news_data_processor(request):
    # 1. Published news uthao
    published_news = News.objects.filter(status='Published')

    # 2. Breaking News
    breaking_news = published_news.filter(is_important=True).order_by('-date')[:20]

    # 3. Check karo kaunse 'district' fields DB mein bhare hue hain
    active_keys = set(published_news.exclude(district__isnull=True).values_list('district', flat=True).distinct())

    dynamic_up_cities = []
    dynamic_big_categories = []

    # 4. UP Districts Dropdown ke liye (Sirf UP ke shehar)
    for eng, hin, city_slug in UP_DISTRICTS:
        if eng in active_keys:
            dynamic_up_cities.append({
                'id': eng, 'name': hin, 'slug': city_slug
            })

    # 5. Badi Categories Dropdown ke liye (National, Sports, etc.)
    for eng, hin, cat_slug in BIG_CATEGORIES:
        if eng in active_keys:
            dynamic_big_categories.append({
                'id': eng, 'name': hin, 'slug': cat_slug
            })

    return {
        'important_news': breaking_news,
        'dynamic_up_cities': dynamic_up_cities,          # Pehla Dropdown: Shehar
        'dynamic_big_categories': dynamic_big_categories, # Doosra Dropdown: Badi News
    }
