
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
    city = os.environ.get("NEBULA_API_CITY", "Lucknow").strip()

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

    rate24 = _number(gold24.get("pricePerGram"))
    rate22 = _number(gold22.get("pricePerGram"))
    rate18 = _number(gold18.get("pricePerGram"))

    if rate24 is None or rate22 is None or rate18 is None:
        raise RuntimeError("NebulaAPI gold rates are missing or invalid.")

    return {
        "city": payload.get("city") or city,
        "yellowGold24K": rate24,
        "yellowGold22K": rate22,
        "yellowGold18K": rate18,
        "silver999": None,
        "platinum999": None,
        "copperPerKg": None,
        "timestamp": payload.get("timestamp") or payload.get("date") or "",
        "gstIncluded": (payload.get("metadata") or {}).get(
            "gst_included", True
        ),
        "source": "nebulaapi-indian-market",
        "authority": payload.get("market", "Indian Market"),
    }


@require_GET
def fsj_live_rates(request):
    try:
        cache_seconds = int(os.environ.get("METALS_CACHE_SECONDS", "600"))
        cache_seconds = max(0, min(cache_seconds, 3600))
    except ValueError:
        cache_seconds = 600

    city_setting = os.environ.get("NEBULA_API_CITY", "Lucknow").strip()
    cache_key = f"fsj_rates_nebula_v1_{city_setting.lower()}"

    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse(cached)

    try:
        rates = _nebula_rates()

        result = {
            "status": "success",
            "city": f"{rates['city']}, Uttar Pradesh",
            "currency": "INR",
            "unit": "per gram",
            "rates": {
                "yellowGold24K": round(float(rates["yellowGold24K"]), 2),
                "yellowGold22K": round(float(rates["yellowGold22K"]), 2),
                "yellowGold18K": round(float(rates["yellowGold18K"]), 2),
                "silver999": None,
                "platinum999": None,
                "copperPerKg": None,
            },
            "timestamp": rates["timestamp"],
            "source": rates["source"],
            "authority": rates["authority"],
            "gstIncluded": rates["gstIncluded"],
            "isLive": True,
        }

        if cache_seconds > 0:
            cache.set(cache_key, result, cache_seconds)

        return JsonResponse(result)

    except (
        HTTPError,
        URLError,
        TimeoutError,
        OSError,
        ValueError,
        RuntimeError,
        json.JSONDecodeError,
    ):
        logger.exception("FS Jewellers NebulaAPI rates request failed.")
        return JsonResponse(
            {
                "status": "error",
                "message": "NebulaAPI gold rates are temporarily unavailable.",
            },
            status=502,
        )
