from .models import News

def important_news(request):
    return {
        'important_news': News.objects.filter(is_important=True).order_by('-date')[:20]
    }

def site_visits(request):
    # Abhi ke liye static value dein taaki error na aaye
    return {"visits": 100}
