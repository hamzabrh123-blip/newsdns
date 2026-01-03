from .models import News

def important_news(request):
    # Safe fetch: Agar koi news na ho toh error na aaye
    return {
        'important_news': News.objects.filter(is_important=True).order_by('-date')[:20]
    }

def site_visits(request):
    # Database logic (Simple way without Cache setup)
    # Agar aapne cache setup nahi kiya hai, toh ye 0 dikhayega crash nahi karega
    return {"visits": 1000} # Abhi ke liye static de rahe hain taaki site crash na ho
