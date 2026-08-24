# shopping/redirects.py

from django.urls import re_path
from django.shortcuts import redirect
from .views import gone_view


# =========================================================
# 1. OLD PRODUCT URL
#
# /product/<slug>/
#        ↓ 301
# /shopping/product/<slug>/
# =========================================================

def old_product_redirect(request, path):

    slug = path.strip("/")

    return redirect(
        f"/shopping/product/{slug}/",
        permanent=True
    )


# =========================================================
# 2. OLD SHOPPING SLUG
#
# /shopping/<slug>/
#        ↓ 301
# /shopping/category/<slug>/
#
# IMPORTANT:
# /shopping/product/<slug>/   -> untouched
# /shopping/category/<slug>/  -> untouched
# =========================================================

def old_shopping_category_redirect(request, path):

    slug = path.strip("/")

    return redirect(
        f"/shopping/category/{slug}/",
        permanent=True
    )


# =========================================================
# OLD URL PATTERNS
# =========================================================

seo_urlpatterns = [

    # =====================================================
    # 1. OLD PRODUCT
    #
    # /product/slug/
    #       ↓ 301
    # /shopping/product/slug/
    # =====================================================

    re_path(
        r'^product/(?P<path>[^/]+)/$',
        old_product_redirect
    ),


    # =====================================================
    # 2. OLD SHOPPING SLUG
    #
    # /shopping/slug/
    #       ↓ 301
    # /shopping/category/slug/
    #
    # /shopping/product/...   NOT TOUCHED
    # /shopping/category/...  NOT TOUCHED
    # =====================================================

    re_path(
        r'^shopping/(?!product/|category/)(?P<path>[^/]+)/$',
        old_shopping_category_redirect
    ),


    # =====================================================
    # 3. EVERYTHING ELSE OLD/UNWANTED -> 410
    #
    # PROTECTED:
    #
    # /shopping/...
    # /search/...
    # /shipping-policy/
    # /about_us/
    # /refund-policy/
    # /terms/
    # /privacy-policy/
    # /contact/
    # /static/store_logo/...
    #
    # /product/<slug>/ is handled above.
    #
    # EVERYTHING ELSE -> 410
    # =====================================================

    re_path(
        r'^(?!'
        r'shopping(?:/|$)|'
        r'search(?:/|$)|'
        r'shipping-policy(?:/|$)|'
        r'about_us(?:/|$)|'
        r'refund-policy(?:/|$)|'
        r'terms(?:/|$)|'
        r'privacy-policy(?:/|$)|'
        r'contact(?:/|$)|'
        r'static/store_logo(?:/|$)|'
        r'product(?:/|$)'
        r').*$',
        gone_view
    ),
]