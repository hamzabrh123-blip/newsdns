from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from urllib.parse import urlparse, parse_qs, urlsplit
from xml.sax.saxutils import escape


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
# ==========================================
# 1. HOME PAGE
# ==========================================
def shop_home(request):
    context = get_base_context()

    sliders = HomeSlider.objects.filter(is_active=True).order_by('?')
    
    # Active sections fetch karo order ke mutabiq
    home_sections = HomeSection.objects.filter(is_active=True).select_related('category').order_by('order')

    # Same heading wale sections ko ek jagah group karne ka logic
    grouped_sections = []
    seen_headings = []

    for section in home_sections:
        h_name = section.heading_name.strip() if section.heading_name else "Featured Collection"
        
        if h_name not in seen_headings:
            seen_headings.append(h_name)
            # Is heading ke jitne bhi active sections hain unhe ek sath list me dalo
            items = [s for s in home_sections if (s.heading_name.strip() if s.heading_name else "Featured Collection") == h_name]
            grouped_sections.append({
                'heading_name': h_name,
                'items': items
            })

    products_list = Product.objects.filter(is_available=True).prefetch_related('variants').defer('long_description').order_by('-created_at')

    paginator = Paginator(products_list, 24)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context.update({
        'sliders': sliders,
        'grouped_sections': grouped_sections,  # 👈 Ab grouped_sections bhej rahe hain
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
                
                # 1. Variant ka Selling Price ya Product ka default Selling Price
                v_selling = None
                if variant:
                    try:
                        if variant.selling_price not in [None, '', 'None', 'null']:
                            v_selling = float(variant.selling_price)
                    except (ValueError, TypeError):
                        v_selling = None

                if v_selling is not None and v_selling > 0:
                    final_selling = v_selling
                else:
                    try:
                        final_selling = float(prod.selling_price) if prod.selling_price not in [None, '', 'None', 'null'] else 0.0
                    except (ValueError, TypeError):
                        final_selling = 0.0

                # 2. Variant ka MRP ya Product ka default MRP (Agar variant me MRP diya hai toh variant se, nahi toh product se)
                v_mrp = None
                if variant:
                    try:
                        raw_vmrp = getattr(variant, 'mrp', None) or getattr(variant, 'mrp_price', None)
                        if raw_vmrp not in [None, '', 'None', 'null']:
                            v_mrp = float(raw_vmrp)
                    except (ValueError, TypeError):
                        v_mrp = None

                if v_mrp is not None and v_mrp > 0:
                    final_mrp = v_mrp
                else:
                    try:
                        raw_pmrp = getattr(prod, 'mrp', None) or getattr(prod, 'mrp_price', None)
                        final_mrp = float(raw_pmrp) if raw_pmrp not in [None, '', 'None', 'null'] else 0.0
                    except (ValueError, TypeError):
                        final_mrp = 0.0

                # --- REMOVE .00 DECIMAL MESS (Convert to Clean Integers) ---
                selling_val = int(round(final_selling)) if final_selling > 0 else 0
                mrp_val = int(round(final_mrp)) if final_mrp > 0 else 0

                # Discount Percentage Calculation
                if mrp_val > 0 and selling_val > 0 and mrp_val > selling_val:
                    disc_pct = round(((mrp_val - selling_val) / mrp_val) * 100)
                else:
                    disc_pct = None

                display_grid.append({
                    'product': prod,
                    'variant': variant if variant else None,
                    'selling_price': selling_val if selling_val > 0 else None,
                    'mrp_price': mrp_val if (mrp_val > selling_val) else None,
                    'calculated_discount': disc_pct  # Sabhi variants ke liye independently calculate hoga
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
# PRODUCT DETAIL (With Prioritized Selected Variant & Clean Pricing)
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
    selected_variant = None

    if variants and selected_variant_id:
        matched_variant = next((v for v in variants if str(v.id) == str(selected_variant_id)), None)
        if matched_variant:
            # Uss specific variant ko list se nikal kar sabse aage (top par) daal do
            variants.remove(matched_variant)
            variants.insert(0, matched_variant)
            selected_variant = matched_variant

    # Agar koi specific variant select nahi hua par variants available hain, toh pehla wala default maan lo
    if not selected_variant and variants:
        selected_variant = variants[0]

    # --- PRICE & DISCOUNT LOGIC (Jaisa Category Page par kiya tha) ---
    v_selling = None
    v_mrp = None

    if selected_variant:
        try:
            if selected_variant.selling_price not in [None, '', 'None', 'null']:
                v_selling = float(selected_variant.selling_price)
        except (ValueError, TypeError):
            v_selling = None

        try:
            raw_vmrp = getattr(selected_variant, 'mrp', None) or getattr(selected_variant, 'mrp_price', None)
            if raw_vmrp not in [None, '', 'None', 'null']:
                v_mrp = float(raw_vmrp)
        except (ValueError, TypeError):
            v_mrp = None

    # Selling Price Fallback (Variant -> Product)
    if v_selling is not None and v_selling > 0:
        final_selling = v_selling
    else:
        try:
            final_selling = float(product.selling_price) if product.selling_price not in [None, '', 'None', 'null'] else 0.0
        except (ValueError, TypeError):
            final_selling = 0.0

    # MRP Fallback (Variant MRP -> Product MRP)
    if v_mrp is not None and v_mrp > 0:
        final_mrp = v_mrp
    else:
        try:
            raw_pmrp = getattr(product, 'mrp', None) or getattr(product, 'mrp_price', None)
            final_mrp = float(raw_pmrp) if raw_pmrp not in [None, '', 'None', 'null'] else 0.0
        except (ValueError, TypeError):
            final_mrp = 0.0

    # Remove .00 Decimal Mess (Convert to Clean Integers)
    selling_val = int(round(final_selling)) if final_selling > 0 else 0
    mrp_val = int(round(final_mrp)) if final_mrp > 0 else 0

    # Discount Percentage Calculation
    disc_pct = None
    if mrp_val > 0 and selling_val > 0 and mrp_val > selling_val:
        disc_pct = round(((mrp_val - selling_val) / mrp_val) * 100)

    context['product'] = product
    context['variants'] = variants  # Ordered list template ke liye
    context['selected_variant'] = selected_variant
    
    # Clean pricing variables template ke liye
    context['display_selling_price'] = selling_val if selling_val > 0 else None
    context['display_mrp_price'] = mrp_val if (mrp_val > selling_val) else None
    context['calculated_discount'] = disc_pct

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
# PRODUCT SEARCH (Exact Match & Single Nearest Fallback Price)
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
        search_query = query.lower().replace('.com', '').strip()

        products = products.filter(
            Q(title__icontains=query) |
            Q(store_name__icontains=query) |
             Q(store_name__iregex=rf'^{search_query}(\.com)?$')
            )
    # ==========================================
    # STORE FILTER
    # ==========================================

    if store:

        store = store.lower().replace(
            '.com',
            ''
        ).strip()

        products = products.filter(store_name__iregex=rf'^{store}(\.com)?$')

    # ==========================================
    # PRICE FILTER (Exact Matching & Safe Nearest Single Lower Price)
    # ==========================================

    filter_price = None

    if max_price and max_price.isdigit():

        target_price = int(max_price)

        # 1. Check for Exact Price Match
        exact_exists = products.filter(variants__selling_price=target_price).exists()

        if exact_exists:
            filter_price = float(target_price)
            products = products.filter(variants__selling_price=target_price).distinct()
        else:
            # 2. Get Nearest Single Lower Price with Safe Type Conversion
            lower_prices = products.filter(
                variants__selling_price__lt=target_price
            ).values_list('variants__selling_price', flat=True).distinct()

            valid_lower_prices = []
            for p in lower_prices:
                try:
                    if p is not None:
                        p_str = str(p).split('~')[0].strip()
                        val = float(p_str)
                        if val > 0 and val < target_price:
                            valid_lower_prices.append(val)
                except (ValueError, TypeError):
                    continue

            if valid_lower_prices:
                valid_lower_prices.sort(reverse=True)
                filter_price = valid_lower_prices[0]
                products = products.filter(variants__selling_price=filter_price).distinct()
            else:
                products = products.none()

    # ==========================================
    # FINAL PRODUCTS SORTING
    # ==========================================

    products_list = products.distinct().order_by(
        '-id'
    )

    # ==========================================
    # ROUND-ROBIN / INTERLEAVED VARIANT GRID LOGIC
    # ==========================================
    display_grid = []
    
    product_variants_pairs = []
    for prod in products_list:
        variants = list(prod.variants.all())
        filtered_variants = []
        
        for v in variants:
            try:
                v_sp = float(str(v.selling_price).split('~')[0].strip()) if v.selling_price not in [None, '', 'None', 'null'] else float(str(prod.selling_price).split('~')[0].strip() if prod.selling_price else 0)
            except (ValueError, TypeError):
                v_sp = float(str(prod.selling_price).split('~')[0].strip() if prod.selling_price else 0)
            
            # Filter strictly by the calculated price (exact or single nearest lower)
            if filter_price is not None:
                if v_sp == filter_price:
                    filtered_variants.append(v)
            else:
                filtered_variants.append(v)
                
        if max_price and max_price.isdigit() and not filtered_variants:
            continue

        if filtered_variants:
            product_variants_pairs.append((prod, filtered_variants))
        elif not max_price:
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
                
                try:
                    v_selling = float(str(variant.selling_price).split('~')[0].strip()) if variant and variant.selling_price not in [None, '', 'None', 'null'] else 0.0
                except (ValueError, TypeError):
                    v_selling = 0.0

                if variant:
                    selling_price = variant.selling_price if (v_selling > 0) else prod.selling_price
                else:
                    selling_price = prod.selling_price
                
                try:
                    mrp_val = float(str(mrp).split('~')[0].strip()) if mrp not in [None, '', 'None', 'null'] else 0.0
                except (ValueError, TypeError):
                    mrp_val = 0.0

                try:
                    selling_val = float(str(selling_price).split('~')[0].strip()) if selling_price not in [None, '', 'None', 'null'] else 0.0
                except (ValueError, TypeError):
                    selling_val = 0.0

                if mrp_val > 0 and selling_val > 0 and mrp_val > selling_val:
                    disc_pct = round(((mrp_val - selling_val) / mrp_val) * 100)
                else:
                    disc_pct = None

                display_grid.append({
                    'product': prod,
                    'variant': variant,
                    'selling_price': selling_price,
                    'calculated_discount': disc_pct
                })

    # ==========================================
    # PAGINATION FOR SEARCH RESULTS
    # ==========================================
    paginator = Paginator(display_grid, 40)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

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
            'products': products_page,
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

from urllib.parse import urlsplit
from xml.sax.saxutils import escape

from django.http import HttpResponse
from .models import Product


def video_sitemap_xml(request):
    site_url = "https://uttarworld.com"

    products = (
        Product.objects.filter(
            is_available=True,
            variants__video_url__isnull=False,
        )
        .exclude(variants__video_url="")
        .distinct()
        .order_by("-created_at")
    )

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset
    xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
    xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
"""

    for product in products:
        product_url = f"{site_url}/shopping/product/{product.slug}/"

        for variant in product.variants.all():
            video_url = (variant.video_url or "").strip()
            thumbnail = (variant.image_url or "").strip()

            if not video_url or not thumbnail:
                continue

            parsed = urlsplit(video_url)

            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                continue

            title = escape(f"{product.title} - Product Video")
            description = escape(
                (product.meta_description or product.title or "Product video").strip()
            )

            xml += f"""
  <url>
    <loc>{escape(product_url)}</loc>
    <video:video>
      <video:thumbnail_loc>{escape(thumbnail)}</video:thumbnail_loc>
      <video:title>{title}</video:title>
      <video:description>{description}</video:description>
      <video:content_loc>{escape(video_url)}</video:content_loc>
    </video:video>
  </url>
"""

    xml += "\n</urlset>"

    return HttpResponse(
        xml,
        content_type="application/xml; charset=utf-8"
    )
