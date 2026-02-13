# ---------------------------------------------------
# 4. SEO & LEGAL (Robots, Ads, Policy)
# ---------------------------------------------------
def sitemap_xml(request):
    items = published_news()[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for n in items:
        xml += f'<url><loc>{SITE_URL}/{n.url_city or "news"}/{n.slug}/</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>'
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request):
    return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml", content_type="text/plain")

def ads_txt(request):
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def privacy_policy(request): return render(request, "mynews/privacy_policy.html", get_common_sidebar_data())
def about_us(request): return render(request, "mynews/about_us.html", get_common_sidebar_data())
