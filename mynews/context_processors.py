from .models import News

def important_news(request):
    return {
        'important_news': News.objects.filter(
            is_important=True,
            status='published'
        )[:5]
    }
