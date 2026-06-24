from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse 
from .models import Product, Category, HomeSlider, DropdownMenu
import re
import random
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q, IntegerField, Value, F, Max, Min
from django.db.models.functions import Cast, Replace, Abs, Coalesce
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

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

@cache_page(60 * 5)

def shop_home(request):
    # 1. Categories aur Sliders ko Random Order mein set kiya
    categories = Category.objects.all().order_by('?') 
    sliders = HomeSlider.objects.filter(is_active=True).order_by('?')
    nav_menus = DropdownMenu.objects.filter(is_active=True).prefetch_related('categories').order_by('order')
    
    query = request.GET.get('q', '').strip()
    max_price = request.GET.get('max_price')
    cat_slug = request.GET.get('cat')

    if query or cat_slug or max_price:
        # Search/Filter wale page par random products
        products = Product.objects.all().prefetch_related('variants').defer('long_description').order_by('?')
        
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
            'categories': categories, 'nav_menus': nav_menus, 'products': page_obj, 
            'sliders': sliders, 'query': query, 'cat_slug': cat_slug,
        })

    else:
        # 2. Main Home Page logic: Random products + 4 item limit per category
        all_products = list(Product.objects.prefetch_related('variants').defer('long_description').order_by('?'))
        homepage_sections = []
        
        for cat in categories:
            # Yahan limit [:4] wapas laga di hai taaki layout na bigde
            cat_products = [p for p in all_products if p.category_id == cat.id][:6]
            
            if cat_products:
                homepage_sections.append({
                    'main_category_name': cat.name,
                    'sub_sections': [{'sub_category_name': cat.name, 'sub_category_slug': cat.slug, 'products': cat_products}]
                })

        return render(request, 'shopping/shop_home.html', {
            'categories': categories, 'nav_menus': nav_menus, 'sliders': sliders,
            'homepage_sections': homepage_sections, 'is_homepage': True,
        })

def category_detail(request, slug):
    # 1. Base context (Menu aur doosri common cheezein yahan se aati hain)
    context = get_base_context() 
    
    # 2. Category fetch karo
    category = get_object_or_404(Category, slug=slug)
    
    # 3. Products filter karo
    products_list = Product.objects.filter(category=category, is_available=True).prefetch_related('variants').order_by('-id')
    
    # 4. Paginator logic
    paginator = Paginator(products_list, 24)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # 5. Context update karo (Menu + Category + Products)
    context.update({
        'category': category,
        'products': products,
    })
    
    return render(request, 'shopping/category_detail.html', context)

def product_detail(request, slug):
    context = get_base_context()
    
    # 1. Product fetch karo
    product = get_object_or_404(Product.objects.prefetch_related('variants'), slug=slug)
    context['product'] = product
    
    # Related products: 12 random items jo current category ke hon
    context['related_products'] = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    ).order_by('?')[:12]  # Limit 12 aur Random Order
    
    return render(request, 'shopping/product_detail.html', context)

def load_more_products(request):
    page = int(request.GET.get('page', 1))
    cat_slug = request.GET.get('cat_slug') # Yahan wo category slug aayega jis par click hua
    
    # Simple query: Agar category slug hai to uska product, warna sab
    products = Product.objects.all().prefetch_related('variants').order_by('?')
    if cat_slug:
        products = products.filter(category__slug=cat_slug)
        
    paginator = Paginator(products, 8) # Ek baar mein 8 products load honge
    page_obj = paginator.get_page(page)
    
    products_html = render_to_string('shopping/product_list_partial.html', {'products': page_obj})
    
    return JsonResponse({
        'html': products_html,
        'has_next': page_obj.has_next(),
    })


# ==========================================
# product search karna hai 
# ==========================================
def product_search(request):
    # 1. Input parameters lo
    query = request.GET.get('q', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    # 2. Product filter karo
    products = Product.objects.filter(is_available=True)

    if query:
        products = products.filter(title__icontains=query)
        
    if max_price and max_price.isdigit():
        products = products.filter(variants__coupons__selling_price__lte=int(max_price))

    products = products.distinct().order_by('-id')

    # 3. GLOBAL DATA FETCH KARO (Navbar aur Slider ke liye)
    # Yeh wahi data hai jo tumhare home page par navbar render karta hai
    nav_menus = DropdownMenu.objects.prefetch_related('categories').all()
    sliders = HomeSlider.objects.all()

    # 4. Ab sab kuch context ke saath pass karo
    return render(request, 'shopping/search_results.html', {
        'products': products,
        'query': query,
        'max_price': max_price,
        'is_search': True,
        'nav_menus': nav_menus,  # Navbar wapas aa jayega
        'sliders': sliders,      # Slider agar chahiye toh
    })

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

