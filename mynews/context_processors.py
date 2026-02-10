from .models import News
from .constants import UP_DISTRICTS, OTHER_CATEGORIES # ✅ Naam wahi rakho jo constants.py mein hai

def news_data_processor(request):
    try:
        # 1. Published news uthao (Sirf wahi news jo live hain)
        published_news = News.objects.filter(status='Published')

        # 2. Breaking News (Top 20)
        breaking_news = published_news.filter(is_important=True).order_by('-date')[:20]

        # 3. DB se wo districts nikalo jin par news live hai
        active_keys = set(published_news.exclude(district__isnull=True).values_list('district', flat=True).distinct())

        dynamic_up_cities = []
        dynamic_big_categories = []

        # 4. UP Districts Dropdown (Sirf wahi shehar dikhenge jinme news hai)
        for eng, hin, city_slug in UP_DISTRICTS:
            if eng in active_keys:
                dynamic_up_cities.append({
                    'id': eng, 
                    'name': hin, 
                    'slug': city_slug
                })

        # 5. Badi Categories Dropdown (National, Sports, etc.)
        for eng, hin, cat_slug in OTHER_CATEGORIES:
            if eng in active_keys:
                dynamic_big_categories.append({
                    'id': eng, 
                    'name': hin, 
                    'slug': cat_slug
                })

        return {
            'important_news': breaking_news,
            'dynamic_up_cities': dynamic_up_cities,          # Dropdown 1: UP Shehar
            'dynamic_big_categories': dynamic_big_categories, # Dropdown 2: Badi News
        }
        
    except Exception as e:
        # Agar koi panga ho toh khali list bhejo taaki site chalti rahe
        return {
            'important_news': [],
            'dynamic_up_cities': [],
            'dynamic_big_categories': [],
        }
