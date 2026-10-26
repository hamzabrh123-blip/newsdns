
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

TROY_OUNCE_GRAMS = Decimal("31.1034768")


def _number(value):
    try:
        result = Decimal(str(value))
        if result.is_finite() and result > 0:
            return result
    except (InvalidOperation, TypeError, ValueError):
        pass
    return None


def _get_json(url):
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "FSJewellersRates/1.0",
        },
        method="GET",
    )

    with urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError("Provider returned an unsuccessful response.")
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, dict):
        raise RuntimeError("Provider returned an unexpected JSON format.")

    return payload


def _gold_api_rates(currency):
    base_url = os.environ.get(
        "GOLD_API_BASE_URL",
        "https://api.gold-api.com/price",
    ).strip().rstrip("/")

    if not base_url.startswith("https://"):
        raise RuntimeError("Gold-API URL must use HTTPS.")

    def fetch(symbol):
        return _get_json(
            f"{base_url}/{symbol}/{currency}"
        )

    gold = fetch("XAU")
    logger.info("Gold-API raw gold response: %s", gold)
    
    silver = fetch("XAG")
    logger.info("Gold-API raw silver response: %s", silver)

    if not gold.get("price") or not silver.get("price"):
        raise RuntimeError("Gold-API gold or silver price is missing.")

    # Gold-API quotes precious metals per troy ounce.
    gold_ounce = _number(gold.get("price"))
    silver_ounce = _number(silver.get("price"))

    if gold_ounce is None or silver_ounce is None:
        raise RuntimeError("Gold-API returned an invalid price.")

    try:
        platinum_data = fetch("XPT")
        platinum_ounce = _number(platinum_data.get("price"))
    except Exception:
        logger.warning("Gold-API platinum rate unavailable.")
        platinum_ounce = None

    return {
        "yellowGold24K": float(gold_ounce / TROY_OUNCE_GRAMS),
        "yellowGold18K": float(
            gold_ounce / TROY_OUNCE_GRAMS * Decimal("0.75")
        ),
        "silver999": float(silver_ounce / TROY_OUNCE_GRAMS),
        "platinum999": (
            float(platinum_ounce / TROY_OUNCE_GRAMS)
            if platinum_ounce is not None else None
        ),
        "copperPerKg": None,
        "timestamp": (
            gold.get("updatedAt")
            or silver.get("updatedAt")
            or ""
        ),
    }


def _metals_dev_rates(currency):
    api_url = os.environ.get(
        "METALS_DEV_API_URL",
        "https://api.metals.dev/v1/latest",
    ).strip()

    api_key = (
        os.environ.get("METALS_DEV_API_KEY", "").strip()
        or os.environ.get("METALS_API_KEY", "").strip()
    )

    if not api_url.startswith("https://"):
        raise RuntimeError("Metals.Dev URL must use HTTPS.")

    if not api_key:
        raise RuntimeError(
            "METALS_DEV_API_KEY is missing in Render Environment."
        )

    params = urlencode({
        "api_key": api_key,
        "currency": currency,
        "unit": "g",
    })

    separator = "&" if "?" in api_url else "?"
    payload = _get_json(f"{api_url}{separator}{params}")

    if payload.get("status") != "success":
        raise RuntimeError("Metals.Dev did not return success.")

    metals = payload.get("metals") or {}

    gold = _number(metals.get("gold"))
    silver = _number(metals.get("silver"))
    platinum = _number(metals.get("platinum"))

    if gold is None or silver is None:
        raise RuntimeError("Metals.Dev gold or silver rate is missing.")

    return {
        "yellowGold24K": float(gold),
        "yellowGold18K": float(gold * Decimal("0.75")),
        "silver999": float(silver),
        "platinum999": float(platinum) if platinum else None,
        "copperPerKg": None,
        "timestamp": payload.get("timestamp", ""),
    }


def _make_response(provider, currency):
    if provider == "gold-api":
        rates = _gold_api_rates(currency)
    elif provider == "metals-dev":
        rates = _metals_dev_rates(currency)
    else:
        raise ValueError(
            "Unsupported provider. Configure gold-api or metals-dev, "
            "or add an adapter for the selected provider."
        )

    timestamp = rates.pop("timestamp", "")

    return {
        "status": "success",
        "city": "Bahraich, Uttar Pradesh",
        "currency": currency,
        "unit": "per gram (except copper)",
        "rates": {
            key: round(value, 2) if value is not None else None
            for key, value in rates.items()
        },
        "timestamp": timestamp,
        "source": provider,
        "isLive": True,
    }


@require_GET
def fsj_live_rates(request):
    provider = os.environ.get(
        "METALS_API_PROVIDER", "gold-api"
    ).strip().lower()

    currency = os.environ.get(
        "METALS_API_CURRENCY", "INR"
    ).strip().upper()

    try:
        cache_seconds = int(
            os.environ.get("METALS_CACHE_SECONDS", "30")
        )
        cache_seconds = max(0, min(cache_seconds, 3600))
    except ValueError:
        cache_seconds = 30

    if len(currency) != 3 or not currency.isalpha():
        return JsonResponse(
            {"status": "error", "message": "Invalid currency configuration."},
            status=503,
        )

    cache_key = f"fsj_rates_v3_{provider}_{currency}"
    cached = cache.get(cache_key)

    if cached is not None:
        return JsonResponse(cached)

    try:
        result = _make_response(provider, currency)

        if cache_seconds:
            cache.set(cache_key, result, cache_seconds)

        return JsonResponse(result)

    except (HTTPError, URLError, TimeoutError, OSError,
            ValueError, RuntimeError):
        logger.exception("FS Jewellers rates provider request failed.")
        return JsonResponse(
            {
                "status": "error",
                "message": "Live metal rates are temporarily unavailable.",
            },
            status=502,
        )
