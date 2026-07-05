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
@cache_page(60 * 5)
def shop_home(request):

    context = get_base_context()

    categories = Category.objects.all().order_by('?')

    sliders = HomeSlider.objects.filter(
        is_active=True
    ).order_by('?')

    # HOME SECTION IMAGE
    home_sections = HomeSection.objects.filter(
        is_active=True
    ).select_related(
        'category'
    ).order_by(
        'order'
    )

    # MIX PRODUCTS
    products_list = Product.objects.filter(
        is_available=True
    ).prefetch_related(
        'variants'
    ).defer(
        'long_description'
    ).order_by('?')

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
# CATEGORY DETAIL
# ==========================================

def category_detail(request, slug):

    context = get_base_context()

    category = get_object_or_404(
        Category,
        slug=slug
    )

    products_list = Product.objects.filter(
        category=category,
        is_available=True
    ).prefetch_related(
        'variants'
    ).order_by(
        '-id'
    )

    paginator = Paginator(
        products_list,
        24
    )

    page_number = request.GET.get('page')

    products = paginator.get_page(
        page_number
    )

    context.update({

        'category': category,

        'products': products,

    })

    return render(
        request,
        'shopping/category_detail.html',
        context
    )

# ==========================================
# PRODUCT DETAIL
# ==========================================

def product_detail(request, slug):

    context = get_base_context()

    product = get_object_or_404(
        Product.objects.prefetch_related(
            'variants'
        ),
        slug=slug
    )

    context['product'] = product

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
        'variants__coupons'
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
                variants__coupons__store_name__icontains=query
            ) |

            Q(
                variants__coupons__store_name__iregex=
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

            variants__coupons__store_name__iregex=
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
            variants__coupons__selling_price=
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

                variants__coupons__selling_price__lt=
                target_price

            ).aggregate(

                max_price=Max(
                    'variants__coupons__selling_price'
                )

            )['max_price']

            # ==========================================
            # HIGHER PRICE
            # ==========================================

            higher_price = products.filter(

                variants__coupons__selling_price__gt=
                target_price

            ).aggregate(

                min_price=Min(
                    'variants__coupons__selling_price'
                )

            )['min_price']

            q_objects = Q()

            # ==========================================
            # LOWER PRODUCTS
            # ==========================================

            if lower_price:

                q_objects |= Q(
                    variants__coupons__selling_price=
                    lower_price
                )

            # ==========================================
            # HIGHER PRODUCTS
            # ==========================================

            if higher_price:

                q_objects |= Q(
                    variants__coupons__selling_price=
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

def about_us(request):

    return render(
        request,
        'shopping/about_us.html',
        get_base_context()
    )


def privacy_policy(request):

    return render(
        request,
        'shopping/privacy_policy.html',
        get_base_context()
    )


def refund_policy(request):

    return render(
        request,
        'shopping/refund_policy.html',
        get_base_context()
    )


def shipping_policy(request):

    return render(
        request,
        'shopping/shipping_policy.html',
        get_base_context()
    )


def terms_of_service(request):

    return render(
        request,
        'shopping/terms.html',
        get_base_context()
    )


def contact_us(request):

    return render(
        request,
        'shopping/contact.html',
        get_base_context()
    )


# ==========================================
# SITEMAP
# ==========================================

def sitemap_shop_xml(request):

    products = Product.objects.filter(
        is_available=True
    ).order_by('-id')

    categories = Category.objects.all()

    site_url = "https://uttarworld.com"

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'

    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    pages = [

        '/',
        '/about/',
        '/privacy-policy/',
        '/refund-policy/',
        '/shipping-policy/',
        '/terms/',
        '/contact/'

    ]

    # ==========================================
    # STATIC PAGES
    # ==========================================

    for page in pages:

        xml += f'''
        <url>
           <loc>{site_url}{page}</loc>
           <changefreq>weekly</changefreq>
           <priority>1.0</priority>
        </url>
        '''

    # ==========================================
    # PRODUCT PAGES
    # ==========================================

    for p in products:

        xml += f'''
        <url>
            <loc>{site_url}/product/{p.slug}/</loc>
            <lastmod>{p.created_at.strftime("%Y-%m-%d")}</lastmod>
            <changefreq>daily</changefreq>
            <priority>0.8</priority>
        </url>
        '''

    # ==========================================
    # CATEGORY PAGES
    # ==========================================

    for c in categories:

        xml += f'''
        <url>
            <loc>{site_url}/category/{c.slug}/</loc>
            <changefreq>weekly</changefreq>
            <priority>0.9</priority>
        </url>
        '''

    xml += '</urlset>'

    return HttpResponse(
        xml,
        content_type="application/xml"
    )