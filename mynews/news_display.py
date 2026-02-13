# ---------------------------------------------------
# 2. HOME & MAIN SECTIONS
# ---------------------------------------------------
def home(request):
    common_data = get_common_sidebar_data()
    all_news = published_news()
    page_number = request.GET.get("page", 1)
    
    context = {
        "other_news": Paginator(all_news, 12).get_page(page_number),
        "page_number": int(page_number),
        **common_data
    }

    if str(page_number) == "1":
        # National: Strict Filter
        national = all_news.filter(Q(category__iexact="National") | Q(category__iexact="Bharat"))[:4]
        
        # World: Strict Filter
        world = all_news.filter(Q(category__iexact="International") | Q(category__iexact="World"))[:4]

        # UP News: Strictly Exclude National/World
        up_news_list = all_news.filter(
            Q(category__icontains="up") | Q(district__isnull=False)
        ).exclude(category__iexact="National").exclude(category__iexact="International")[:12]

        context.update({
            "top_5_highlights": all_news.filter(show_in_highlights=True)[:12] or all_news[:12],
            "national_news": national,
            "world_news": world,
            "up_news": up_news_list,
        })
    return render(request, "mynews/home.html", context)

def district_news(request, district):
    dist_name = district.strip()
    news_list = published_news().filter(
        Q(district__iexact=dist_name) | Q(category__iexact=dist_name)
    )
    return render(request, "mynews/district_news.html", {
        "district": dist_name,
        "page_obj": Paginator(news_list, 15).get_page(request.GET.get("page")),
        **get_common_sidebar_data()
    })
