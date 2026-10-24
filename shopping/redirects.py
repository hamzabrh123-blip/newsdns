
# shopping/redirects.py

from django.urls import re_path
from django.shortcuts import redirect

from .views import gone_view
from .models import Product, Category


# =========================================================
# 1. OLD PRODUCT URL
# /product/<slug>/ -> /shopping/product/<slug>/
# =========================================================

def old_product_redirect(request, path):
    slug = path.strip("/")

    # Sirf existing product ko redirect karo
    product = Product.objects.filter(
        slug__iexact=slug
    ).first()

    if product:
        return redirect(
            f"/shopping/product/{product.slug}/",
            permanent=True
        )

    # Product nahi mila to 410 Gone
    return gone_view(request)


# =========================================================
# 2. OLD CATEGORY URL
# /category/<slug>/ -> /shopping/category/<slug>/
# =========================================================

def old_category_redirect(request, path):
    slug = path.strip("/")

    category = Category.objects.filter(
        slug__iexact=slug
    ).first()

    if category:
        return redirect(
            f"/shopping/category/{category.slug}/",
            permanent=True
        )

    # Category nahi mili to 410 Gone
    return gone_view(request)


# =========================================================
# 3. OLD SHOPPING SLUG
# /shopping/<old-slug>/
# Product ya Category ko identify karke redirect karo
# =========================================================

def old_shopping_category_redirect(request, path):
    slug = path.strip("/")

    product = Product.objects.filter(
        slug__iexact=slug
    ).first()

    if product:
        return redirect(
            f"/shopping/product/{product.slug}/",
            permanent=True
        )

    category = Category.objects.filter(
        slug__iexact=slug
    ).first()

    if category:
        return redirect(
            f"/shopping/category/{category.slug}/",
            permanent=True
        )

    return gone_view(request)


# =========================================================
# OLD URL PATTERNS
# IMPORTANT: shopping/urls.py mein inhe last mein rakho
# =========================================================

seo_urlpatterns = [

    # -----------------------------------------------------
    # 1. OLD PRODUCT URL
    # -----------------------------------------------------
    re_path(
        r"^product/(?P<path>[^/]+)/$",
        old_product_redirect
    ),

    # -----------------------------------------------------
    # 2. OLD CATEGORY URL
    # -----------------------------------------------------
    re_path(
        r"^category/(?P<path>[^/]+)/$",
        old_category_redirect
    ),

    # -----------------------------------------------------
    # 3. OLD SHOPPING SLUG
    # -----------------------------------------------------
    re_path(
        r"^shopping/(?!product/|category/)(?P<path>[^/]+)/$",
        old_shopping_category_redirect
    ),

    # -----------------------------------------------------
    # 4. EVERYTHING ELSE OLD/UNWANTED -> 410 GONE
    # -----------------------------------------------------
    re_path(
        r"^(?!"
        r"shopping(?:/|$)|"
        r"search(?:/|$)|"
        r"shipping-policy(?:/|$)|"
        r"about_us(?:/|$)|"
        r"refund-policy(?:/|$)|"
        r"terms(?:/|$)|"
        r"privacy-policy(?:/|$)|"
        r"contact(?:/|$)|"
        r"static/store_logo(?:/|$)|"
        r"product(?:/|$)|"
        r"category(?:/|$)"
        r").*$",
        gone_view
    ),
]
