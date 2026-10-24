import ipaddress
import requests

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Product, ProductVariant, ShopNowClick


@require_POST
def track_shop_now_click(request):
    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")

    try:
        product = Product.objects.get(pk=product_id)
    except (Product.DoesNotExist, TypeError, ValueError):
        return JsonResponse({"error": "Product not found"}, status=404)

    variant = None
    if variant_id:
        variant = ProductVariant.objects.filter(
            pk=variant_id,
            product=product,
        ).first()

    store_name = (product.store_name or "").strip()
    city = ""
    country = request.META.get("HTTP_CF_IPCOUNTRY", "")

    ip = (
        request.META.get("HTTP_CF_CONNECTING_IP")
        or request.META.get("REMOTE_ADDR", "")
    )

    try:
        ipaddress.ip_address(ip)
        response = requests.get(
            f"https://ipwho.is/{ip}",
            timeout=2,
        )
        data = response.json()

        if data.get("success"):
            city = data.get("city") or ""
            country = data.get("country") or country
    except Exception:
        pass

    ShopNowClick.objects.create(
        product=product,
        variant=variant,
        store_name=store_name,
        city=city,
        country=country,
    )

    return JsonResponse({"ok": True})
