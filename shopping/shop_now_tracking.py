import ipaddress
import requests
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Product, ProductVariant, ShopNowClick, VisitorClickLog


@csrf_exempt
@require_POST
def track_visitor_or_shop_event(request):
    """
    Ye ek hi endpoint dono kaam karega:
    1. Home/Site Visit log karega (Platform, State, City ke sath)
    2. Shop Now Click log karega (Product, Variant, Platform, State, City ke sath)
    """
    try:
        # Request body JSON ya POST form data dono handle kar lega
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        event_type = data.get("event_type", "HOME_VISIT") # HOME_VISIT ya SHOP_CLICK
        product_id = data.get("product_id")
        variant_id = data.get("variant_id")
        traffic_source = data.get("traffic_source", "Direct / Browser")
        device_type = data.get("device_type", "Mobile")

        product = None
        variant = None
        store_name = ""
        product_name = ""

        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
                store_name = (product.store_name or "").strip()
                product_name = product.title
            except (Product.DoesNotExist, TypeError, ValueError):
                pass

        if variant_id and product:
            variant = ProductVariant.objects.filter(
                pk=variant_id,
                product=product,
            ).first()

        # Client ki Real IP nikalna (Cloudflare + Standard Fallback)
        ip = (
            request.META.get("HTTP_CF_CONNECTING_IP")
            or request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR", "")
        )

        city = "Unknown"
        state = "Unknown"
        country = request.META.get("HTTP_CF_IPCOUNTRY", "IN")

        # IP Geolocation check (Sirf India ke traffic ko process karenge)
        try:
            ipaddress.ip_address(ip)
            if ip and ip != "127.0.0.1" and ip != "localhost":
                response = requests.get(f"https://ipwho.is/{ip}", timeout=2)
                data_geo = response.json()

                if data_geo.get("success"):
                    country_name = data_geo.get("country", "")
                    # India filter
                    if "india" in country_name.lower() or country == "IN":
                        city = data_geo.get("city") or "Unknown"
                        state = data_geo.get("region") or "Unknown"
                    else:
                        return JsonResponse({"status": "ignored", "reason": "non-indian traffic"})
        except Exception:
            pass

        # 1. New Advanced VisitorClickLog Model mein save karo
        VisitorClickLog.objects.create(
            event_type=event_type,
            state=state,
            city=city,
            traffic_source=traffic_source,
            device_type=device_type,
            product_name=product_name if product_name else "Homepage / Site",
            ip_address=ip if ip else None
        )

        # 2. Agar Shop Click hai, toh purana ShopNowClick legacy model bhi maintain rakho
        if event_type == "SHOP_CLICK" and product:
            ShopNowClick.objects.create(
                product=product,
                variant=variant,
                store_name=store_name,
                city=city,
                country=country,
            )

        return JsonResponse({"status": "success", "city": city, "state": state, "source": traffic_source})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)