from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse # HttpResponse इम्पोर्ट करना न भूलें
from .models import Product, Category, HomeSlider

# ... तेरे पुराने व्यूज (shop_home, category_detail, product_detail) यहाँ रहेंगे ...

# 4. SHOPPING SITEMAP (Manual XML Style)
def sitemap_shop_xml(request):
    try:
        # सिर्फ वही प्रोडक्ट्स जो स्टॉक में हैं या उपलब्ध हैं
        # .order_by('-id') ताकि लेटेस्ट माल सैटमैप में भी ऊपर रहे
        products = Product.objects.filter(is_available=True).order_by('-id')
        
        # साइट का यूआरएल (बिना स्लैश के)
        site_url = "https://uttarworld.com"
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for p in products:
            # प्रोडक्ट का फुल यूआरएल: domain + shop + slug
            # अगर तेरा URL स्ट्रक्चर अलग है तो यहाँ बदल लेना
            product_url = f"{site_url}/shop/product/{p.slug}/"
            # तारीख के लिए created_at इस्तेमाल कर रहे हैं
            last_mod = p.created_at.strftime("%Y-%m-%d") if hasattr(p, 'created_at') else "2026-05-01"
            
            xml += f'  <url>\n    <loc>{product_url}</loc>\n    <lastmod>{last_mod}</lastmod>\n  </url>\n'
            
        xml += '</urlset>'
        return HttpResponse(xml, content_type="application/xml")
    except Exception as e:
        return HttpResponse(str(e), content_type="text/plain")