from django.shortcuts import render
from .models import News

def news_list(request):
    news_items = News.objects.order_by('-date')
    return render(request, 'mynews/news_list.html', {'news_items': news_items})
