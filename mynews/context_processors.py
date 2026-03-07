from .models import News, SidebarWidget
from .constants import UP_DISTRICTS, OTHER_CATEGORIES

def news_data_processor(request):
    # 1. Default values (ताकि अगर DB एरर आए तो भी टेम्प्लेट क्रैश न हो)
    context = {
        'important_news': [],
        'dynamic_up_cities': [],
        'dynamic_big_categories': [],
        'sidebar_widgets': [], 
        'sidebar_latest_news': [], 
    }
    
    try:
        # 2. Published news (सबसे पहले चेक करें कि News टेबल है या नहीं)
        published_news = News.objects.filter(status='Published')

        # 3. Breaking News
        context['important_news'] = published_news.filter(is_important=True).order_by('-date')[:20]

        # 4. Sidebar Widgets (इसे अलग try में रखा है ताकि ये News को न रोके)
        try:
            context['sidebar_widgets'] = SidebarWidget.objects.filter(active=True).order_by('order')
        except Exception as e:
            print(f"SidebarWidget Table Missing: {e}")
            context['sidebar_widgets'] = []

        # 5. Sidebar Latest News
        context['sidebar_latest_news'] = published_news.order_by('-date')[:10]

        # 6. Active Categories/Districts
        active_keys = set(published_news.exclude(district__isnull=True).values_list('district', flat=True).distinct())

        # 7. UP Districts Dropdown (Indentation Fixed)
        for item in UP_DISTRICTS:
            try:
                if len(item) >= 3:
                    eng, hin, city_slug = item[0], item[1], item[2]
                    if eng in active_keys:
                        context['dynamic_up_cities'].append({
                            'id': eng, 'name': hin, 'slug': city_slug
                        })
            except:
                continue

        # 8. OTHER Categories Dropdown
        for item in OTHER_CATEGORIES:
            try:
                if len(item) >= 3:
                    eng, hin, cat_slug = item[0], item[1], item[2]
                    if eng in active_keys:
                        context['dynamic_big_categories'].append({
                            'id': eng, 'name': hin, 'slug': cat_slug
                        })
            except:
                continue

    except Exception as e:
        print(f"Context Processor Main Error: {e}")
        
    return context

def site_visits(request):
    return {'site_visits_count': 0}
