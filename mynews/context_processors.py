from .models import News

def site_visits(request):
    """
    Render ka error fix karne ke liye:
    Agar visitor count ka table nahi hai toh abhi sirf 0 bhej rahe hain.
    """
    return {'site_visits': 0}

def news_data_processor(request):
    """
    Sare important data ko ek hi processor mein combine kar diya
    taaki bar-bar database par load na pade.
    """
    # 1. Important News (Breaking News)
    breaking_news = News.objects.filter(is_important=True).order_by('-date')[:20]

    # 2. Dynamic UP Cities Logic
    active_districts = News.objects.values_list('district', flat=True).distinct()
    
    dynamic_up_cities = []
    for item in News.LOCATION_DATA:
        # item[0]=Key (Agra), item[1]=Hindi (आगरा), item[2]=Category (UP)
        if item[0] in active_districts and item[2] == 'UP':
            dynamic_up_cities.append({
                'id': item[0],
                'name': item[1]
            })

    return {
        'important_news': breaking_news,
        'dynamic_up_cities': dynamic_up_cities,
    }
