from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse 
from .models import Product, Category, HomeSlider

# 1. होम पेज (यह रेंडर को नहीं मिल रहा था)
def shop_home(request):
    categories = Category.objects.all()
    # लेटेस्ट प्रोडक्ट्स सबसे ऊपर
    products = Product.objects.all().order_by('-id')
    sliders = HomeSlider.objects.filter(is_active=True).order_by('-id')
    
    return render(request, 'shopping/shop_home.html', {
        'categories': categories,
        'products': products,
        'sliders': sliders
    })

# 2. कैटेगरी डिटेल पेज
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category).order_by('-id')
    categories = Category.objects.all() 
    
    return render(request, 'shopping/shop_home.html', {
        'category': category,
        'products': products,
        'categories': categories
    })

# 3. प्रोडक्ट डिटेल पेज
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    categories = Category.objects.all() 
    
    return render(request, 'shopping/product_detail.html', {
        'product': product,
        'categories': categories
    })

# 4. सैटमैप फंक्शन
def sitemap_shop_xml(request):
    try:
        products = Product.objects.filter(is_available=True).order_by('-id')
        site_url = "https://uttarworld.com"
        
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for p in products:
            product_url = f"{site_url}/shop/product/{p.slug}/"
            last_mod = p.created_at.strftime("%Y-%m-%d") if hasattr(p, 'created_at') else "2026-05-01"
            xml += f'  <url>\n    <loc>{product_url}</loc>\n    <lastmod>{last_mod}</lastmod>\n  </url>\n'
            
        xml += '</urlset>'
        return HttpResponse(xml, content_type="application/xml")
    except Exception as e:
        return HttpResponse(str(e), content_type="text/plain")