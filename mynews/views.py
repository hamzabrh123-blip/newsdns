from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from .models import News, Comment


# 🏠 Homepage View
def home(request):
    query = request.GET.get("q")
    if query:
        news_list = News.objects.filter(title__icontains=query)
    else:
        news_list = News.objects.filter(
            models.Q(category__iexact='International') | models.Q(is_important=True)
        ).order_by('-date')[:12]

    print("DEBUG: total news =", News.objects.count())
    print("DEBUG: international =", News.objects.filter(category__iexact='International').count())
    print("DEBUG: important =", News.objects.filter(is_important=True).count())
    print("DEBUG: home news =", news_list.count())

    important = News.objects.filter(is_important=True)[:5]

    return render(request, "mynews/home.html", {
        "news_list": news_list,
        "important": important
    })


# 🇮🇳 National News Page
def national_news(request):
    news_list = News.objects.filter(category='National').order_by('-date')
    return render(request, "mynews/national_news.html", {
        "news_list": news_list
    })


# 📰 News Detail View
def news_detail(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    comments = Comment.objects.filter(news=news).order_by('-date')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        comment_text = request.POST.get('comment')

        if name and comment_text:
            Comment.objects.create(
                news=news,
                name=name,
                email=email,
                comment=comment_text
            )
            return redirect('news_detail', news_id=news.id)

    return render(request, 'mynews/news_detail.html', {
        'news': news,
        'comments': comments
    })


# 🗺️ District-wise News Page
def district_news(request, district):
    news_list = News.objects.filter(district__iexact=district).order_by('-date')
    return render(request, 'mynews/district_news.html', {
        'district': district,
        'news_list': news_list,
    })


# 📄 Static Pages
def about(request):
    return render(request, 'mynews/about.html')

def contact(request):
    return render(request, 'mynews/contact.html')
