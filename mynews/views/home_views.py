from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import News 
from .base import get_common_sidebar_data, published_news

# --- 1. HOME VIEW ---
def home(request):
    all_news = published_news()
    page_number = request.GET.get("page", 1)
    
    # Dusre pages ke liye sirf normal list dikhegi
    context = {
        "other_news": Paginator(all_news, 12).get_page(page_number),
        "page_number": int(page_number),
        **get_common_sidebar_data()
    }

    # Section sirf Page 1 par dikhenge
    if str(page_number) == "1":
        # 1. National News Filter
        national = all_news.filter(Q(category__icontains="National") | Q(category__icontains="Bharat"))[:4]
        
        # 2. World News Filter
        world = all_news.filter(Q(category__icontains="International") | Q(category__icontains="World"))[:4]
        
        # 3. UP News (SABSE ZAROORI FIX)
        # Isme se hum National aur World ko Strictly nikaal rahe hain
        up_news = all_news.filter(
            Q(category__icontains="up") | 
            Q(category__icontains="uttar") | 
            Q(district__isnull=False)
        ).exclude(
            Q(category__icontains="National") | 
            Q(category__icontains="Bharat") | 
            Q(category__icontains="World") | 
            Q(category__icontains="International")
        ).distinct()[:12]

        context.update({
            "top_5_highlights": all_news.filter(show_in_highlights=True)[:12] or all_news[:12],
            "national_news": national,
            "world_news": world,
            "up_news": up_news,
        })
        
    return render(request, "mynews/home.html", context)

# --- Baki Views (Sahi Logic ke saath) ---
def district_news(request, district):
    dist_name = district.strip()
    news_list = published_news().filter(Q(district__iexact=dist_name) | Q(category__iexact=dist_name)).order_by('-date')
    return render(request, "mynews/district_news.html", {
        "district": dist_name,
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })

def national_view(request):
    news_list = published_news().filter(Q(category__icontains="National") | Q(category__icontains="Bharat")).order_by('-date')
    return render(request, "mynews/district_news.html", {
        "district": "देश / भारत",
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })

def world_view(request):
    news_list = published_news().filter(Q(category__icontains="International") | Q(category__icontains="World")).order_by('-date')
    return render(request, "mynews/district_news.html", {
        "district": "दुनिया / विदेश",
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })

def up_news_view(request):
    news_list = published_news().filter(
        Q(category__icontains="up") | Q(category__icontains="uttar") | Q(district__isnull=False)
    ).exclude(
        Q(category__icontains="National") | Q(category__icontains="World")
    ).order_by('-date')
    
    return render(request, "mynews/district_news.html", {
        "district": "उत्तर प्रदेश न्यूज़",
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })

def ent_view(request):
    news_list = published_news().filter(Q(category__icontains="Bollywood") | Q(category__icontains="Manoranjan") | Q(category__icontains="Entertainment")).order_by('-date')
    return render(request, "mynews/district_news.html", {
        "district": "मनोरंजन",
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })
