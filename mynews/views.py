def news_detail(request, slug):
    # 🔹 1. News fetch
    news = get_object_or_404(News, slug=slug)

    # 🔹 2. Sidebar: latest news (current exclude)
    sidebar_news = (
        News.objects
        .exclude(id=news.id)
        .order_by('-id')[:50]
    )

    # 🔹 Debug (safe)
    if settings.DEBUG:
        print("SIDEBAR COUNT:", len(sidebar_news))

    # 🔹 3. YouTube embed fix
    if news.youtube_url:
        if "watch?v=" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace(
                "watch?v=", "embed/"
            )
        elif "youtu.be/" in news.youtube_url:
            news.youtube_url = news.youtube_url.replace(
                "youtu.be/", "www.youtube.com/embed/"
            )

    # 🔹 4. Comments
    comments = (
        Comment.objects
        .filter(news=news)
        .order_by("-date")
    )

    # 🔹 5. Render
    return render(
        request,
        "mynews/news_detail.html",
        {
            "news": news,
            "sidebar_news": sidebar_news,
            "comments": comments,
        }
    )
