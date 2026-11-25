# shopping/redirects.py

from django.urls import re_path
from django.shortcuts import redirect

from .views import gone_view
from .models import Product, Category


def _find_product_by_slug(slug):
    if not slug:
        return None
    return Product.objects.filter(slug__iexact=slug).first()


def _find_category_by_slug(slug):
    if not slug:
        return None
    return Category.objects.filter(slug__iexact=slug).first()


# =========================================================
# 1. OLD PRODUCT URL
# /product/<slug>/ -> /shopping/product/<slug>/
# =========================================================

def old_product_redirect(request, path):
    slug = (path or "").strip("/")
    product = _find_product_by_slug(slug)

    if product:
        return redirect(f"/shopping/product/{product.slug}/", permanent=True)

    return gone_view(request)


# =========================================================
# 2. OLD CATEGORY URL
# /category/<slug>/ -> /shopping/category/<slug>/
# =========================================================

def old_category_redirect(request, path):
    slug = (path or "").strip("/")
    category = _find_category_by_slug(slug)

    if category:
        return redirect(f"/shopping/category/{category.slug}/", permanent=True)

    return gone_view(request)


# =========================================================
# 3. OLD SHOPPING SLUG
# /shopping/<old-slug>/ -> product ya category ya 410
# =========================================================

def old_shopping_slug_redirect(request, path):
    slug = (path or "").strip("/")

    product = _find_product_by_slug(slug)
    if product:
        return redirect(f"/shopping/product/{product.slug}/", permanent=True)

    category = _find_category_by_slug(slug)
    if category:
        return redirect(f"/shopping/category/{category.slug}/", permanent=True)

    return gone_view(request)


# =========================================================
# OLD URL PATTERNS
# IMPORTANT: shopping/urls.py mein active routes ke baad rakho
# =========================================================

seo_urlpatterns = [
    re_path(
        r"^product/(?P<path>[^/]+)/?$",
        old_product_redirect,
    ),
    re_path(
        r"^category/(?P<path>[^/]+)/?$",
        old_category_redirect,
    ),
    re_path(
        r"^shopping/(?!product(?:/|$)|category(?:/|$))(?P<path>[^/]+)/?$",
        old_shopping_slug_redirect,
    ),
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
        r"static(?:/|$)|"
        r"control-panel(?:/|$)|"
        r"ckeditor(?:/|$)|"
        r"feedback(?:/|$)|"
        r"favicon\.ico$|"
        r"google21a82f00fad0f9b3\.html$|"
        r"product(?:/|$)|"
        r"category(?:/|$)"
        r").*$",
        gone_view,
    ),
]