from django.http import HttpResponse
# Purana: from .models import News (Yeh error de raha tha)
# Naya:
from mynews.models import News
from mynews.config import SITE_URL

def ads_txt(request): 
    return HttpResponse("google.com, pub-3171847065256414, DIRECT, f08c47fec0942fa0", content_type="text/plain")

def robots_txt(request):
    # Aapne robots_txt urls.py mein likha hai, toh uska function yahan hona chahiye
    content = "User-agent: *\nDisallow: /admin/\nSitemap: " + SITE_URL + "/sitemap.xml"
    return HttpResponse(content, content_type="text/plain")

def sitemap_xml(request):
    items = News.objects.exclude(slug__isnull=True).order_by('-date')[:500]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for n in items:
        city = n.url_city if n.url_city else "news"
        xml += f" <url><loc>{SITE_URL}/{city}/{n.slug}.html</loc></url>\n"
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")