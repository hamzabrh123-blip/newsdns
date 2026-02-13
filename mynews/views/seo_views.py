from django.http import HttpResponse
from django.shortcuts import render
from .base import get_common_sidebar_data, published_news

SITE_URL = "https://uttarworld.com"

def sitemap_xml(request):
    items = published_news()[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for n in items:
        xml += f'<url><loc>{SITE_URL.rstrip("/")}/{n.url_city or "news"}/{n.slug.strip()}/</loc><lastmod>{n.date.strftime("%Y-%m-%d")}</lastmod></url>'
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")

def robots_txt(request):
    return HttpResponse(f"User-Agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml", content_type="text/plain")

def ads_txt(request):
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")
