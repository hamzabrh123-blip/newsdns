from .models import News

def important_news(request):
    return {
        'important_news': News.objects.filter(is_important=True).order_by('-date')[:20]
    }

def active_cities_processor(request):
    # 1. Check karo kin districts/categories mein news hai
    active_districts = News.objects.values_list('district', flat=True).distinct()
    
    # 2. News.LOCATION_DATA se filter karo
    # item[0]=Key, item[1]=Hindi Name, item[2]=Category
    dynamic_up_cities = []
    
    for item in News.LOCATION_DATA:
        # Sirf tab add karo jab uski news ho AUR wo 'UP' category ka ho
        if item[0] in active_districts and item[2] == 'UP':
            dynamic_up_cities.append({
                'id': item[0],
                'name': item[1]
            })

    return {
        'dynamic_up_cities': dynamic_up_cities,
        'important_news': News.objects.filter(is_important=True).order_by('-date')[:20]
    }
