from .models import News
from .constants import UP_DISTRICTS, OTHER_CATEGORIES

def news_data_processor(request):
    # Default values taaki crash na ho
    context = {
        'important_news': [],
        'dynamic_up_cities': [],
        'dynamic_big_categories': [],
    }
    
    try:
        # 1. Sabse pehle Published news nikalo
        published_news = News.objects.filter(status='Published')

        # 2. Breaking News (Top 20)
        context['important_news'] = published_news.filter(is_important=True).order_by('-date')[:20]

        # 3. DB se wo districts/categories nikalo jinme news hai
        # .distinct() bahut zaruri hai yahan
        active_keys = set(published_news.exclude(district__isnull=True).values_list('district', flat=True).distinct())

        # 4. UP Districts Dropdown (Sirf wahi jinme news hai)
        for item in UP_DISTRICTS:
            try:
                eng, hin, city_slug = item
                if eng in active_keys:
                    context['dynamic_up_cities'].append({
                        'id': eng, 
                        'name': hin, 
                        'slug': city_slug
                    })
            except (ValueError, IndexError):
                continue # Agar kisi item mein data kam hai toh use skip karo

        # 5. Badi Categories Dropdown
        for item in OTHER_CATEGORIES:
            try:
                eng, hin, cat_slug = item
                if eng in active_keys:
                    context['dynamic_big_categories'].append({
                        'id': eng, 
                        'name': hin, 
                        'slug': cat_slug
                    })
            except (ValueError, IndexError):
                continue

    except Exception as e:
        # Render log mein error dikhega par site chalti rahegi
        print(f"Context Processor Error: {e}")
        
    return context

def site_visits(request):
    return {
        'site_visits_count': 0 
    }
