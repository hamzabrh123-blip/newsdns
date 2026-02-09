from .models import News

def site_visits(request):
    # अभी के लिए 0, बाद में यहाँ आप विजिटर काउंटर का लॉजिक लिख सकते हैं
    return {'site_visits': 0}

def news_data_processor(request):
    # ब्रेकिंग न्यूज़ का लॉजिक सही है
    breaking_news = News.objects.filter(is_important=True).order_by('-date')[:20]
    
    # एक्टिव जिलों की लिस्ट
    active_districts = News.objects.values_list('district', flat=True).distinct()
    
    dynamic_up_cities = []
    
    # Fix: LOCATION_DATA में 'UP' कीवर्ड नहीं है, इसलिए slug या ID का इस्तेमाल करें
    # हम सिर्फ उन शहरों को उठाएंगे जिनकी न्यूज़ डेटाबेस में मौजूद है
    for item in News.LOCATION_DATA:
        # item[0] = English Name (e.g. 'Agra')
        # item[1] = Hindi Name (e.g. 'आगरा')
        if item[0] in active_districts:
            dynamic_up_cities.append({
                'id': item[0], 
                'name': item[1],
                'slug': item[2] # slug का इस्तेमाल URL बनाने में होगा
            })

    return {
        'important_news': breaking_news,
        'dynamic_up_cities': dynamic_up_cities,
    }
