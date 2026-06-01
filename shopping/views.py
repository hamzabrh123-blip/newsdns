from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse 
from .models import Product, Category, HomeSlider, DropdownMenu
import re
from django.db.models import Q, IntegerField, Value, F, Max, Min
from django.db.models.functions import Cast, Replace, Abs
from django.core.paginator import Paginator

# ==========================================
# HELPER: Nav Data & AdSense
# ==========================================
def get_base_context():
    return {
        'nav_menus': DropdownMenu.objects.filter(is_active=True).prefetch_related('categories').order_by('order'),
        'adsense_client': 'ca-pub-3171847065256414'
    }

# ==========================================
# 1. CORE SHOPPING VIEWS
# ==========================================

def shop_home(request):
    categories = Category.objects.all()
    sliders = HomeSlider.objects.filter(is_active=True).order_by('-id')
    nav_menus = DropdownMenu.objects.filter(is_active=True).prefetch_related('categories').order_by('order')
    
    query = request.GET.get('q', '').strip()
    max_price = request.GET.get('max_price')
    cat_slug = request.GET.get('cat')

    if query or cat_slug or max_price:
        products = Product.objects.all().prefetch_related('variants').defer('long_description').order_by('-id')
        
        if cat_slug:
            products = products.filter(category__slug=cat_slug)
            
        if query:
            search_terms = re.split(r'[.\s]+', query)
            for term in search_terms:
                if term:
                    products = products.filter(title__icontains=term)

        products_with_price = products.annotate(
            clean_price=Replace(Replace('price_display', Value(','), Value('')), Value('-'), Value('')),
        ).annotate(
            price_as_int=Cast('clean_price', output_field=IntegerField())
        )
        
        paginator = Paginator(products_with_price, 24) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'shopping/shop_home.html', {
            'categories': categories, 
            'nav_menus': nav_menus, 
            'products': page_obj, 
            'sliders': sliders, 
            'query': query, 
            'cat_slug': cat_slug,
        })

    else:
        homepage_sections = []
        for cat in categories:
            cat_products = Product.objects.filter(category=cat).prefetch_related('variants').defer('long_description').order_by('-id')[:4]
            if cat_products.exists():
                homepage_sections.append({
                    'main_category_name': cat.name,
                    'sub_sections': [{
                        'sub_category_name': cat.name,
                        'sub_category_slug': cat.slug,
                        'products': cat_products
                    }]
                })

        fallback_products = None
        if not homepage_sections:
            fallback_products = Product.objects.all().prefetch_related('variants').defer('long_description').order_by('-id')[:12]

        return render(request, 'shopping/shop_home.html', {
            'categories': categories,
            'nav_menus': nav_menus,
            'sliders': sliders,
            'homepage_sections': homepage_sections, 
            'fallback_products': fallback_products, 
            'is_homepage': True,
        })

def category_detail(request, slug):
    context = get_base_context()
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category).prefetch_related('variants')
    paginator = Paginator(products, 24)
    context.update({'category': category, 'products': paginator.get_page(request.GET.get('page'))})
    return render(request, 'shopping/category_detail.html', context)

def product_detail(request, slug):
    context = get_base_context()
    context['product'] = get_object_or_404(Product.objects.prefetch_related('variants'), slug=slug)
    return render(request, 'shopping/product_detail.html', context)

def product_search(request):
    context = get_base_context()
    query = request.GET.get('q', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    
    products = Product.objects.all().order_by('-id')
    
    products = products.annotate(
        clean_price=Replace(Replace('price_display', Value(','), Value('')), Value('-'), Value('')),
    ).annotate(price_as_int=Cast('clean_price', output_field=IntegerField()))

    if query:
        if query.isdigit():
            products = products.filter(price_as_int=int(query))
        else:
            search_terms = re.split(r'[.\s]+', query)
            for term in search_terms:
                if term:
                    products = products.filter(title__icontains=term)
    
    if max_price and max_price.isdigit():
        val = int(max_price)
        exact_match = products.filter(price_as_int=val)
        if exact_match.exists():
            products = exact_match
        else:
            products = products.annotate(diff=Abs(F('price_as_int') - val)).order_by('diff')

    paginator = Paginator(products, 24)
    context.update({
        'products': paginator.get_page(request.GET.get('page')), 
        'query': query,
        'is_search': True 
    })
    
    return render(request, 'shopping/shop_home.html', context)

# ==========================================
# 2. ELITE POLICY & ABOUT PAGES
# ==========================================

def about_us(request): return render(request, 'shopping/about_us.html', get_base_context())
def privacy_policy(request): return render(request, 'shopping/privacy_policy.html', get_base_context())
def refund_policy(request): return render(request, 'shopping/refund_policy.html', get_base_context())
def shipping_policy(request): return render(request, 'shopping/shipping_policy.html', get_base_context())
def terms_of_service(request): return render(request, 'shopping/terms.html', get_base_context())
def contact_us(request): return render(request, 'shopping/contact.html', get_base_context())

# ==========================================
# 3. SITEMAP
# ==========================================

def sitemap_shop_xml(request):
    products = Product.objects.filter(is_available=True).order_by('-id')
    categories = Category.objects.all()
    site_url = "https://uttarworld.com"
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    pages = ['/', '/about/', '/privacy-policy/', '/refund-policy/', '/shipping-policy/', '/terms/', '/contact/']
    for page in pages:
        xml += f'  <url><loc>{site_url}{page}</loc><changefreq>monthly</changefreq></url>\n'
    for p in products:
        xml += f'  <url><loc>{site_url}/product/{p.slug}/</loc><lastmod>{p.created_at.strftime("%Y-%m-%d")}</lastmod></url>\n'
    for c in categories:
        xml += f'  <url><loc>{site_url}/category/{c.slug}/</loc><changefreq>weekly</changefreq></url>\n'
    xml += '</urlset>'
    return HttpResponse(xml, content_type="application/xml")