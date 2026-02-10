from .models import News
from .constants import UP_DISTRICTS, OTHER_CATEGORIES 

def news_data_processor(request):
    try:
        # 1. Published news uthao
        published_news = News.objects.filter(status='Published')

        # 2. Breaking News (Top 20)
        important_news = published_news.filter(is_important=True).order_by('-date')[:20]

        # 3. DB se wo districts nikalo jin par news live hai
        active_keys = set(published_news.exclude(district__isnull=True).values_list('district', flat=True).distinct())

        dynamic_up_cities = []
        dynamic_big_categories = []

        # 4. UP Districts Dropdown logic (Safe Unpacking)
        if UP_DISTRICTS:
            for item in UP_DISTRICTS:
                if len(item) >= 3: # Check ki kam se kam 3 value hain
                    eng, hin, city_slug = item[0], item[1], item[2]
                    if eng in active_keys:
                        dynamic_up_cities.append({
                            'id': eng, 
                            'name': hin, 
                            'slug': city_slug
                        })

        # 5. Badi Categories Dropdown logic (Safe Unpacking)
        if OTHER_CATEGORIES:
            for item in OTHER_CATEGORIES:
                if len(item) >= 3:
                    eng, hin, cat_slug = item[0], item[1], item[2]
                    if eng in active_keys:
                        dynamic_big_categories.append({
                            'id': eng, 
                            'name': hin, 
                            'slug': cat_slug
                        })

        return {
            'important_news': important_news,
            'dynamic_up_cities': dynamic_up_cities,
            'dynamic_big_categories': dynamic_big_categories,
        }
        
    except Exception as e:
        # Agar error aaye bhi, toh ye khali data bhejega par SITE CRASH NAHI HONE DEGA
        print(f"Processor Error: {e}") 
        return {
            'important_news': [],
            'dynamic_up_cities': [],
            'dynamic_big_categories': [],
        }

def site_visits(request):
    return {
        'site_visits_count': 0 
    }
