from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from django.db.models import (
    Q,
    IntegerField,
    Value,
    Max,
    Min
)

from django.db.models.functions import (
    Cast,
    Replace
)

import re
import random

from .models import (
    Product,
    Category,
    HomeSlider,
    DropdownMenu,
    HomeSection,
    HomePageSEO
)

def gone_view(request, *args, **kwargs):
    return HttpResponse("Page Gone", status=410)


# ==========================================
# HELPER: NAV DATA
# ==========================================

def get_base_context():

    home_seo = HomePageSEO.objects.first()

    return {

        'nav_menus': DropdownMenu.objects.filter(
            is_active=True
        ).prefetch_related(
            'categories'
        ).order_by(
            'order'
        ),

        'adsense_client': 'ca-pub-3171847065256414',

        'home_seo': home_seo,

    }


# ==========================================
# 1. HOME PAGE
# ==========================================
def shop_home(request):

    context = get_base_context()

    categories = Category.objects.filter( products__is_available=True ).distinct().order_by('name')
    
    sliders = HomeSlider.objects.filter(is_active=True).order_by('?')

    # HOME SECTION IMAGE
    home_sections = HomeSection.objects.filter( is_active=True).select_related(   'category' ).order_by(  'order')

    # MIX PRODUCTS
    products_list = Product.objects.filter( is_available=True).prefetch_related('variants' ).defer( 'long_description').order_by('-created_at')

    # PAGINATION
    paginator = Paginator(
        products_list,
        24
    )

    page_number = request.GET.get('page')

    products = paginator.get_page(
        page_number
    )

    context.update({

        'categories': categories,

        'sliders': sliders,

        'home_sections': home_sections,

        'products': products,

        'is_homepage': True,

    })

    return render(
        request,
        'shopping/shop_home.html',
        context
    )


# ==========================================
# CATEGORY DETAIL (Fixed Interleaved Variants & Paginator)
# ==========================================

def category_detail(request, slug):
    context = get_base_context()

    category = get_object_or_404(
        Category,
        slug=slug
    )

    # Products fetch karo aur variants prefetch karo
    products_list = Product.objects.filter(
        category=category,
        is_available=True
    ).prefetch_related(
        'variants'
    ).order_by(
        '-id'
    )

    # --- ROUND-ROBIN / INTERLEAVED VARIANT GRID LOGIC ---
    display_grid = []
    
    product_variants_pairs = []
    for prod in products_list:
        variants = list(prod.variants.all())
        if variants:
            product_variants_pairs.append((prod, variants))
        else:
            product_variants_pairs.append((prod, [None]))

    max_variants = max([len(v) for p, v in product_variants_pairs], default=0)
    
    for i in range(max_variants):
        for prod, variants in product_variants_pairs:
            if i < len(variants):
                variant = variants[i]
                
                # --- PROPER PRICE & DISCOUNT PERCENTAGE CALCULATION ---
                disc_pct = None
                selling_price = None
                mrp = prod.mrp_price
                
                if variant:
                    # Pehle variant ka price dekho, agar nahi hai toh product ka default selling price uthao
                    selling_price = variant.selling_price if (variant.selling_price and variant.selling_price > 0) else prod.selling_price
                    
                    if mrp and selling_price and mrp > selling_price:
                        disc_pct = round(((mrp - selling_price) / mrp) * 100)

                display_grid.append({
                    'product': prod,
                    'variant': variant,
                    'selling_price': selling_price,
                    'calculated_discount': disc_pct  # Ab sabhi ke liye discount barabar calculate hoga
                })

    paginator = Paginator(
        display_grid,
        100 
    )

    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context.update({
        'category': category,
        'products': products_page,
    })

    return render(
        request,
        'shopping/category_detail.html',
        context
    )
# ==========================================
# PRODUCT DETAIL (With Prioritized Selected Variant)
# ==========================================

def product_detail(request, slug):
    context = get_base_context()

    product = get_object_or_404(
        Product.objects.prefetch_related(
            'variants'
        ),
        slug=slug
    )

    # Variants ki list bana lo taaki hum usko reorder kar sakein
    variants = list(product.variants.all())

    # Check karo ki category page se koi variant ID (?v=XYZ) aayi hai ya nahi
    selected_variant_id = request.GET.get('v')

    if variants and selected_variant_id:
        matched_variant = next((v for v in variants if str(v.id) == str(selected_variant_id)), None)
        if matched_variant:
            # Uss specific variant ko list se nikal kar sabse aage (top par) daal do
            variants.remove(matched_variant)
            variants.insert(0, matched_variant)

    context['product'] = product
    context['variants'] = variants  # Yeh ab ordered list jayegi template mein

    context['related_products'] = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    ).order_by('?')[:12]

    return render(
        request,
        'shopping/product_detail.html',
        context
    )

# ==========================================
# LOAD MORE PRODUCTS
# ==========================================

def load_more_products(request):

    page = int(
        request.GET.get('page', 1)
    )

    cat_slug = request.GET.get(
        'cat_slug'
    )

    products = Product.objects.all().prefetch_related(
        'variants'
    ).order_by('?')

    if cat_slug:

        products = products.filter(
            category__slug=cat_slug
        )

    paginator = Paginator(
        products,
        8
    )

    page_obj = paginator.get_page(
        page
    )

    products_html = render_to_string(
        'shopping/product_list_partial.html',
        {
            'products': page_obj
        }
    )

    return JsonResponse({

        'html': products_html,
        'has_next': page_obj.has_next(),

    })


# ==========================================
# PRODUCT SEARCH
# ==========================================

def product_search(request):

    # ==========================================
    # INPUTS
    # ==========================================

    query = request.GET.get(
        'q',
        ''
    ).strip()

    max_price = request.GET.get(
        'max_price',
        ''
    ).strip()

    store = request.GET.get(
        'store',
        ''
    ).strip()

    # ==========================================
    # BASE QUERY
    # ==========================================

    products = Product.objects.filter(
        is_available=True
    ).prefetch_related(
        'variants'
    )

    # ==========================================
    # SEARCH FILTER
    # ==========================================

    if query:

        search_query = query.lower().replace(
            '.com',
            ''
        ).strip()

        products = products.filter(

            Q(
                title__icontains=query
            ) |

            Q(
                variants__store_name__icontains=query
            ) |

            Q(
                variants__store_name__iregex=
                rf'^{search_query}(\.com)?$'
            )

        )

    # ==========================================
    # STORE FILTER
    # ==========================================

    if store:

        store = store.lower().replace(
            '.com',
            ''
        ).strip()

        products = products.filter(

            variants__store_name__iregex=
            rf'^{store}(\.com)?$'

        )

    # ==========================================
    # PRICE FILTER
    # ==========================================

    if max_price and max_price.isdigit():

        target_price = int(max_price)

        # ==========================================
        # EXACT PRICE PRODUCTS
        # ==========================================

        exact_products = products.filter(
            variants__selling_price=
            target_price
        ).distinct()

        # ==========================================
        # EXACT MATCH FOUND
        # ==========================================

        if exact_products.exists():

            products = exact_products

        else:

            # ==========================================
            # LOWER PRICE
            # ==========================================

            lower_price = products.filter(

                variants__selling_price__lt=
                target_price

            ).aggregate(

                max_price=Max(
                    'variants__selling_price'
                )

            )['max_price']

            # ==========================================
            # HIGHER PRICE
            # ==========================================

            higher_price = products.filter(

                variants__selling_price__gt=
                target_price

            ).aggregate(

                min_price=Min(
                    'variants__selling_price'
                )

            )['min_price']

            q_objects = Q()

            # ==========================================
            # LOWER PRODUCTS
            # ==========================================

            if lower_price:

                q_objects |= Q(
                    variants__selling_price=
                    lower_price
                )

            # ==========================================
            # HIGHER PRODUCTS
            # ==========================================

            if higher_price:

                q_objects |= Q(
                    variants__selling_price=
                    higher_price
                )

            products = products.filter(
                q_objects
            ).distinct()

    # ==========================================
    # FINAL PRODUCTS
    # ==========================================

    products = products.distinct().order_by(
        '-id'
    )

    # ==========================================
    # GLOBAL DATA
    # ==========================================

    nav_menus = DropdownMenu.objects.prefetch_related(
        'categories'
    ).all()

    sliders = HomeSlider.objects.all()

    # ==========================================
    # RENDER
    # ==========================================

    return render(
        request,
        'shopping/search_results.html',
        {
            'products': products,
            'query': query,
            'max_price': max_price,
            'store': store,
            'is_search': True,
            'nav_menus': nav_menus,
            'sliders': sliders,
        }
    )


# ==========================================
# STATIC PAGES
# ==========================================

def about_us(request): return render(  request,  'shopping/about_us.html',  get_base_context() )


def privacy_policy(request): return render(  request, 'shopping/privacy_policy.html', get_base_context() )


def refund_policy(request): return render( request, 'shopping/refund_policy.html', get_base_context() )

def shipping_policy(request): return render(request, 'shopping/shipping_policy.html', get_base_context() )

def terms_of_service(request): return render( request, 'shopping/terms.html',get_base_context())

def contact_us(request): return render( request, 'shopping/contact.html', get_base_context())

# ==========================================
# SITEMAP
# ==========================================
def sitemap_shop_xml(request):

    products = Product.objects.filter(
        is_available=True
    ).order_by("-created_at")

    categories = Category.objects.filter(
        products__is_available=True
    ).distinct().order_by("name")

    site_url = "https://uttarworld.com"

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # Home
    xml += f"""
    <url>
        <loc>{site_url}/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    """

    # Categories
    for c in categories:
        xml += f"""
        <url>
            <loc>{site_url}/shopping/category/{c.slug}/</loc>
            <changefreq>weekly</changefreq>
            <priority>0.9</priority>
        </url>
        """

    # Products
    for p in products:
        xml += f"""
        <url>
            <loc>{site_url}/shopping/product/{p.slug}/</loc>
            <lastmod>{p.created_at.strftime("%Y-%m-%d")}</lastmod>
            <changefreq>weekly</changefreq>
            <priority>0.8</priority>
        </url>
        """

    xml += "</urlset>"

    return HttpResponse(
        xml,
        content_type="application/xml"
    )