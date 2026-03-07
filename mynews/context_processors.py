from .models import News, SidebarWidget
from .constants import UP_DISTRICTS, OTHER_CATEGORIES

def news_data_processor(request):
    # Default values taaki crash na ho
    context = {
        'important_news': [],
        'dynamic_up_cities': [],
        'dynamic_big_categories': [],
        'sidebar_widgets': [], # Naya: Admin se Ads/Banners ke liye
        'sidebar_latest_news': [], # Naya: Sidebar ki news list ke liye
    }
    
    try:
        # 1. Published news nikalo
        published_news = News.objects.filter(status='Published')

        # 2. Breaking News (Top 20)
        context['important_news'] = published_news.filter(is_important=True).order_by('-date')[:20]

        # 3. Sidebar Widgets (Admin se manage hone wale ads aur sections)
        context['sidebar_widgets'] = SidebarWidget.objects.filter(active=True).order_by('order')
        
        # 4. Sidebar Latest News (Sidebar ke widgets ke liye data)
        context['sidebar_latest_news'] = published_news.order_by('-date')[:10]

        # 5. DB se wo districts/categories nikalo jinme news hai
        active_keys = set(published_news.exclude(district__isnull=True).values_list('district', flat=True).distinct())

        # 6. UP Districts Dropdown (Sirf wahi jinme news hai)
        for item in UP_DISTRICTS:
            try:
                eng, hin, city_slug = item
                if eng in active_keys:
                    context['dynamic_up_cities'].append({
                        'id': eng, 'name': hin, 'slug': city_slug
                    })
            except: continue

        # 7. Badi Categories Dropdown
        for item in OTHER_CATEGORIES:
            try:
                eng, hin, cat_slug = item
                if eng in active_keys:
                    context['dynamic_big_categories'].append({
                        'id': eng, 'name': hin, 'slug': cat_slug
                    })
            except: continue

    except Exception as e:
        print(f"Context Processor Error: {e}")
        
    return context

def site_visits(request):
    return {'site_visits_count': 0}
