from .models import News

def important_news(request):
    return {
        'important_news': News.objects.filter(is_important=True).order_by('-date')[:20]
    }

def active_cities_processor(request):
    # 1. Poora data map kar lo (Hindi names ke liye)
    all_location_map = {item[0]: item[1] for item in News.LOCATION_DATA}
    all_category_map = {item[0]: item[2] for item in News.LOCATION_DATA}
    
    # 2. Kin categories/districts mein news hai (Unique list)
    active_keys = News.objects.values_list('district', flat=True).distinct()
    
    # 3. Alag-alag list banao taaki Navbar mein kachra na ho
    dynamic_up_cities = []
    other_categories = []

    for key in active_keys:
        if key in all_location_map:
            item = {'id': key, 'name': all_location_map[key]}
            # Agar category 'UP' hai toh UP wale dropdown mein dalo
            if all_category_map.get(key) == 'UP':
                dynamic_up_cities.append(item)
            # Warna National/International wale menu mein dalo
            else:
                other_categories.append(item)

    return {
        'dynamic_up_cities': dynamic_up_cities,
        'other_categories': other_categories, # National, Sports, etc. ke liye
    }
