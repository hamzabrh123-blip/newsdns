from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
# Double dot (..) kyunki models.py ek level upar hai
from ..models import News 
from .base import get_common_sidebar_data, published_news

# --- 1. HOME VIEW ---
def home(request):
    all_news = published_news()
    page_number = request.GET.get("page", 1)
    
    context = {
        "other_news": Paginator(all_news, 12).get_page(page_number),
        "page_number": int(page_number),
        **get_common_sidebar_data()
    }

    if str(page_number) == "1":
        context.update({
            "top_5_highlights": all_news.filter(show_in_highlights=True)[:12] or all_news[:12],
            "national_news": all_news.filter(Q(category__iexact="National") | Q(category__iexact="Bharat"))[:4],
            "world_news": all_news.filter(Q(category__iexact="International") | Q(category__iexact="World"))[:4],
            "up_news": all_news.filter(Q(category__icontains="up") | Q(district__isnull=False)).exclude(category__iexact="National").exclude(category__iexact="International")[:12],
        })
    return render(request, "mynews/home.html", context)

# --- 2. DISTRICT / CATEGORY VIEW ---
def district_news(request, district):
    dist_name = district.strip()
    news_list = published_news().filter(Q(district__iexact=dist_name) | Q(category__iexact=dist_name))
    return render(request, "mynews/district_news.html", {
        "district": dist_name,
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })

# --- 3. NATIONAL PAGE VIEW (Jo urls.py mein hai) ---
def national_view(request):
    news_list = published_news().filter(Q(category__iexact="National") | Q(category__iexact="Bharat"))
    return render(request, "mynews/district_news.html", {
        "district": "देश / भारत",
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })

# --- 4. WORLD PAGE VIEW ---
def world_view(request):
    news_list = published_news().filter(Q(category__iexact="International") | Q(category__iexact="World"))
    return render(request, "mynews/district_news.html", {
        "district": "दुनिया / विदेश",
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })

# --- 5. UP NEWS PAGE VIEW ---
def up_news_view(request):
    news_list = published_news().filter(Q(category__icontains="up") | Q(district__isnull=False)).exclude(category__iexact="National").exclude(category__iexact="International")
    return render(request, "mynews/district_news.html", {
        "district": "उत्तर प्रदेश न्यूज़",
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })

# --- 6. ENTERTAINMENT VIEW ---
def ent_view(request):
    news_list = published_news().filter(Q(category__icontains="Bollywood") | Q(category__icontains="Manoranjan"))
    return render(request, "mynews/district_news.html", {
        "district": "मनोरंजन",
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })
