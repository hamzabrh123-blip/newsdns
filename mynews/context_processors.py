from .models import News

def important_news(request):
    return {
        'important_news': News.objects.filter(is_important=True).order_by('-date')[:20]
    }

def site_visits(request):
    # Future mein yahan hit counter laga sakte hain
    return {"visits": 1524} 

def active_cities_processor(request):
    # 1. UP Districts ki list model se uthao
    up_keys = [item[0] for item in News.UP_CITIES]
    
    # 2. Check karo kin districts mein news hai (Unique districts)
    active_districts = News.objects.filter(district__in=up_keys).values_list('district', flat=True).distinct()
    
    # 3. Map keys to Hindi Names (e.g., 'Lucknow' -> 'लखनऊ')
    city_map = dict(News.UP_CITIES)
    active_cities_list = [{'id': d, 'name': city_map.get(d)} for d in active_districts]

    return {
        'dynamic_up_cities': active_cities_list
    }