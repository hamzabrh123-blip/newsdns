# shopping/redirects.py

from django.urls import re_path
from django.shortcuts import redirect
from .views import gone_view
from .models import Product, Category


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
# 2. OLD SHOPPING SLUG (Smart Dual Check: Product or Category)
# =========================================================

def old_shopping_category_redirect(request, path):
    slug = path.strip("/")

    # Pehle database mein check kar ki kya ye ek valid Product hai?
    product = Product.objects.filter(slug__iexact=slug).first()
    if product:
        return redirect(
            f"/shopping/product/{product.slug}/",
            permanent=True
        )

    # Phir check kar ki kya ye ek valid Category hai?
    category = Category.objects.filter(slug__iexact=slug).first()
    if category:
        return redirect(
            f"/shopping/category/{category.slug}/",
            permanent=True
        )

    # Agar na product hai na category, tabhi 410 Gone bhej
    return gone_view(request)


# =========================================================
# OLD URL PATTERNS
# =========================================================

seo_urlpatterns = [

    # =====================================================
    # 1. OLD PRODUCT
    # =====================================================
    re_path(
        r'^product/(?P<path>[^/]+)/$',
        old_product_redirect
    ),

    # =====================================================
    # 2. OLD SHOPPING SLUG
    # =====================================================
    re_path(
        r'^shopping/(?!product/|category/)(?P<path>[^/]+)/$',
        old_shopping_category_redirect
    ),

    # =====================================================
    # 3. EVERYTHING ELSE OLD/UNWANTED -> 410
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