import json
import logging
import os
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

NEBULA_API_URL = "https://workspace.nebulaapi.com/gold_price"


def _number(value):
    try:
        result = Decimal(str(value))
        if result.is_finite() and result > 0:
            return result
    except (InvalidOperation, TypeError, ValueError):
        pass
    return None


def _get_json(url, api_key):
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "x-api-key": api_key,
            "User-Agent": "FSJewellersRates/1.0",
        },
        method="GET",
    )

    with urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError("NebulaAPI returned an unsuccessful response.")
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, dict):
        raise RuntimeError("NebulaAPI returned an unexpected JSON format.")

    return payload


def _nebula_rates():
    api_key = os.environ.get("NEBULA_API_KEY", "").strip()
    city = os.environ.get("NEBULA_API_CITY", "Bahraich").strip()

    if not api_key:
        raise RuntimeError("NEBULA_API_KEY is missing in Render Environment.")

    if not city:
        raise RuntimeError("NEBULA_API_CITY is empty.")

    params = urlencode({"city": city})
    payload = _get_json(f"{NEBULA_API_URL}?{params}", api_key)

    if payload.get("success") is not True:
        raise RuntimeError("NebulaAPI did not return success.")

    prices = payload.get("prices") or {}
    gold24 = prices.get("gold24k") or {}
    gold22 = prices.get("gold22k") or {}
    gold18 = prices.get("gold18k") or {}
    silver_data = prices.get("silver") or {}

    rate24 = _number(gold24.get("pricePerGram"))
    rate22 = _number(gold22.get("pricePerGram"))
    rate18 = _number(gold18.get("pricePerGram"))
    rate_silver = _number(silver_data.get("pricePerGram"))

    if rate24 is None:
        raise RuntimeError("NebulaAPI 24K gold rate is missing.")

    if rate22 is None:
        rate22 = round(rate24 * Decimal("0.916"), 2)

    if rate18 is None:
        rate18 = round(rate24 * Decimal("0.75"), 2)

    return {
        "city": payload.get("city") or city,
        "yellowGold24K": rate24,
        "yellowGold22K": rate22,
        "yellowGold18K": rate18,
        "silver999": rate_silver,
        "platinum999": None,
        "copperPerKg": None,
        "timestamp": payload.get("timestamp") or payload.get("date") or "",
        "gstIncluded": (payload.get("metadata") or {}).get("gst_included", True),
        "source": "nebulaapi-indian-market",
        "authority": payload.get("market", "Indian Market"),
    }


@require_GET
def fsj_live_rates(request):
    city_setting = os.environ.get("NEBULA_API_CITY", "Bahraich").strip()
    cache_key = f"fsj_rates_nebula_v1_{city_setting.lower()}"
    fallback_cache_key = f"fsj_rates_permanent_fallback_{city_setting.lower()}"

    try:
        rates = _nebula_rates()

        result = {
            "status": "success",
            "city": f"{rates['city']}, Uttar Pradesh",
            "currency": "INR",
            "unit": "per gram",
            "rates": {
                "yellowGold24K": float(rates["yellowGold24K"]),
                "yellowGold22K": float(rates["yellowGold22K"]),
                "yellowGold18K": float(rates["yellowGold18K"]),
                "silver999": float(rates["silver999"]) if rates["silver999"] else 0.0,
                "platinum999": None,
                "copperPerKg": None,
            },
            "timestamp": rates["timestamp"],
            "source": rates["source"],
            "authority": rates["authority"],
            "gstIncluded": rates["gstIncluded"],
            "isLive": True,
        }

        # 1. Normal cache (10 mins)
        cache.set(cache_key, result, 600)
        
        # 2. Permanent Fallback Cache (Yeh expire nahi hoga jab tak server restart ya clear na ho)
        cache.set(fallback_cache_key, result, None)

        return JsonResponse(result)

    except Exception as e:
        logger.exception("FS Jewellers NebulaAPI request failed. Checking cache fallback.")
        
        # 🛡️ FALLBACK: Agar API fail ho jaye, toh cache se aakhri successful data utha lo!
        last_known = cache.get(fallback_cache_key)
        if last_known:
            last_known["isLive"] = False  # App ko pata chal jayega ki live API down hai
            last_known["source"] = "fallback-cache"
            return JsonResponse(last_known)

        return JsonResponse(
            {
                "status": "error",
                "message": "NebulaAPI rates unavailable and no cache found.",
            },
            status=502,
        )