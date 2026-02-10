from .models import News
from .constants import UP_DISTRICTS, OTHER_CATEGORIES 

def news_data_processor(request):
    try:
        # 1. Published news uthao
        published_news = News.objects.filter(status='Published')

        # 2. Breaking News (Top 20) - scroll ke liye
        breaking_news = published_news.filter(is_important=True).order_by('-date')[:20]

        # 3. DB se wo districts/categories nikalo jin par news live hai
        active_keys = set(published_news.exclude(district__isnull=True).values_list('district', flat=True).distinct())

        dynamic_up_cities = []
        dynamic_big_categories = []

        # 4. UP Districts Dropdown logic
        for eng, hin, city_slug in UP_DISTRICTS:
            if eng in active_keys:
                dynamic_up_cities.append({
                    'id': eng, 
                    'name': hin, 
                    'slug': city_slug
                })

        # 5. Badi Categories Dropdown logic
        for eng, hin, cat_slug in OTHER_CATEGORIES:
            if eng in active_keys:
                dynamic_big_categories.append({
                    'id': eng, 
                    'name': hin, 
                    'slug': cat_slug
                })

        return {
            'important_news': breaking_news,
            'dynamic_up_cities': dynamic_up_cities,
            'dynamic_big_categories': dynamic_big_categories,
        }
        
    except Exception as e:
        return {
            'important_news': [],
            'dynamic_up_cities': [],
            'dynamic_big_categories': [],
        }

# ✅ Ye function add kar diya taaki tera RENDER wala error khatam ho jaye
def site_visits(request):
    return {
        'site_visits_count': 0  # Abhi ke liye 0, error nahi aayega ab
    }
