from .models import News

def site_visits(request):
    return {'site_visits': 0}

def news_data_processor(request):
    breaking_news = News.objects.filter(is_important=True).order_by('-date')[:20]
    active_districts = News.objects.values_list('district', flat=True).distinct()
    
    dynamic_up_cities = []
    for item in News.LOCATION_DATA:
        if item[0] in active_districts and item[2] == 'UP':
            dynamic_up_cities.append({'id': item[0], 'name': item[1]})

    return {
        'important_news': breaking_news,
        'dynamic_up_cities': dynamic_up_cities,
    }
