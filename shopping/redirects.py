# shopping/redirects.py

from django.urls import re_path
from django.shortcuts import redirect
from .views import gone_view
from .models import Product


# =========================================================
# OLD PRODUCT URL -> CURRENT PRODUCT URL
# =========================================================

def old_product_redirect(request, path):
    """
    Old product URL ko current shopping product URL par
    301 Permanent Redirect karta hai.

    /product/slug/
        ->
    /shopping/product/slug/

    /shopping/slug/
        ->
    /shopping/product/slug/

    Product available hai -> 301
    Product nahi mila -> 410 Gone
    """

    slug = path.strip("/")

    product = Product.objects.filter(
        slug=slug,
        is_available=True
    ).first()

    if product:
        return redirect(
            f"/shopping/product/{product.slug}/",
            permanent=True
        )

    return gone_view(request)


# =========================================================
# OLD URL PATTERNS
# =========================================================

seo_urlpatterns = [

    # =====================================================
    # 1. OLD PRODUCT URL
    #
    # /product/slug/
    #        ↓ 301
    # /shopping/product/slug/
    # =====================================================

    re_path(
        r'^product/(?P<path>[^/]+)/$',
        old_product_redirect
    ),


    # =====================================================
    # 2. OLD SHOPPING PRODUCT URL
    #
    # /shopping/slug/
    #        ↓ 301
    # /shopping/product/slug/
    #
    # IMPORTANT:
    # /shopping/product/...
    # /shopping/category/...
    # ko ye rule touch nahi karega.
    # =====================================================

    re_path(
        r'^shopping/(?!product/|category/)(?P<path>[^/]+)/$',
        old_product_redirect
    ),


    # =====================================================
    # 3. OLD CATEGORY URLS
    #
    # /category/anything/
    #        ↓ 410 Gone
    #
    # Isse purani category URLs automatically cover hongi.
    # =====================================================

    re_path(
        r'^category/.*$',
        gone_view
    ),


    # =====================================================
    # 4. OLD NEWS / CITY / DISTRICT / CONTENT URLS
    #
    # Ye purane content prefixes 410 Gone honge.
    #
    # IMPORTANT:
    # (?i) use nahi kiya gaya hai, kyunki Django URL
    # resolver ke saath "Non-reversible reg-exp portion"
    # error aa sakta hai.
    # =====================================================

    re_path(
        r'^(?:'

        # General / News
        r'ai|'
        r'news|'
        r'n|'
        r'national|'
        r'district|'
        r'other-state|'
        r'other-states|'
        r'uttar-pradesh|'
        r'uttarpradesh|'
        r'up-national|'

        # Technology / Google / AI
        r'technology|'
        r'google|'

        # Entertainment
        r'bollywood|'
        r'hollywood|'

        # International
        r'international|'
        r'toronto-canada|'

        # Market / Sports
        r'market|'
        r'market-news|'
        r'sports|'

        # Uttar Pradesh districts / cities
        r'agra|'
        r'amethi|'
        r'auraiya|'
        r'baghpat|'
        r'bahraich|'
        r'balrampur|'
        r'banda|'
        r'barabanki|'
        r'basti|'
        r'bijnor|'
        r'chandauli|'
        r'deoria|'
        r'delhi|'
        r'etah|'
        r'farrukhabad|'
        r'firozabad|'
        r'gautam-buddha-nagar|'
        r'ghaziabad|'
        r'gonda|'
        r'gorakhpur|'
        r'gorakhpur-lucknow|'
        r'hapur|'
        r'hyderabad|'
        r'jhansi|'
        r'kanpur|'
        r'kanpur-dehat|'
        r'kanpur-nagar|'
        r'kannauj|'
        r'kaushambi|'
        r'lucknow|'
        r'mahoba|'
        r'mainpuri|'
        r'mathura|'
        r'meerut|'
        r'moradabad|'
        r'mumbai|'
        r'new-delhi|'
        r'pilibhit|'
        r'prayagraj|'
        r'rae-bareli|'
        r'rampur|'
        r'saharanpur|'
        r'shamli|'
        r'shahjahanpur|'
        r'shravasti|'
        r'sitapur|'
        r'sultanpur|'
        r'sambhal|'
        r'ujjain|'
        r'varanasi|'
        r'goa'

        r')/.*$',
        gone_view
    ),
]