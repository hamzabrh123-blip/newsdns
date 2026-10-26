
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

IBJA_API_URL = "https://api.metals.dev/v1/metal/authority"


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
            raise RuntimeError(
                "Metals.Dev returned an unsuccessful response."
            )
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, dict):
        raise RuntimeError(
            "Metals.Dev returned an unexpected JSON format."
        )

    return payload


def _metals_dev_rates(currency):
    api_url = os.environ.get(
        "METALS_DEV_API_URL",
        IBJA_API_URL,
    ).strip()

    api_key = (
        os.environ.get("METALS_DEV_API_KEY", "").strip()
        or os.environ.get("METALS_API_KEY", "").strip()
    )

    if not api_url.startswith("https://"):
        raise RuntimeError("Metals.Dev URL must use HTTPS.")

    if not api_key:
        raise RuntimeError(
            "Metals.Dev API key is missing in Render Environment."
        )

    params = urlencode({
        "api_key": api_key,
        "authority": "ibja",
        "currency": currency,
        "unit": "g",
    })

    separator = "&" if "?" in api_url else "?"
    payload = _get_json(f"{api_url}{separator}{params}")

    if payload.get("status") != "success":
        raise RuntimeError(
            "Metals.Dev IBJA request did not return success."
        )

    if payload.get("authority", "").lower() != "ibja":
        raise RuntimeError(
            "Metals.Dev did not confirm IBJA as the authority."
        )

    rates = payload.get("rates") or {}

    gold = _number(rates.get("ibja_gold"))
    silver = _number(rates.get("ibja_silver"))

    if gold is None or silver is None:
        raise RuntimeError(
            "IBJA gold or silver rate is missing or invalid."
        )

    return {
        "yellowGold24K": float(gold),
        "yellowGold18K": float(
            gold * Decimal("0.75")
        ),
        "silver999": float(silver),
        "platinum999": None,
        "copperPerKg": None,
        "timestamp": payload.get("timestamp", ""),
    }


def _make_response(provider, currency):
    if provider != "metals-dev":
        raise ValueError(
            "Unsupported provider. Set METALS_API_PROVIDER=metals-dev."
        )

    rates = _metals_dev_rates(currency)
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
        "source": "metals-dev-ibja",
        "authority": "ibja",
        "isLive": True,
    }


@require_GET
def fsj_live_rates(request):
    provider = os.environ.get(
        "METALS_API_PROVIDER", "metals-dev"
    ).strip().lower()

    currency = os.environ.get(
        "METALS_API_CURRENCY", "INR"
    ).strip().upper()

    try:
        cache_seconds = int(
            os.environ.get("METALS_CACHE_SECONDS", "90")
        )
        cache_seconds = max(0, min(cache_seconds, 3600))
    except ValueError:
        cache_seconds = 90

    if len(currency) != 3 or not currency.isalpha():
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid currency configuration.",
            },
            status=503,
        )

    if provider != "metals-dev":
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "Configure METALS_API_PROVIDER=metals-dev "
                    "to use IBJA rates."
                ),
            },
            status=503,
        )

    cache_key = f"fsj_rates_ibja_v1_{currency}"

    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse(cached)

    try:
        result = _make_response(provider, currency)

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
        logger.exception(
            "FS Jewellers IBJA rates request failed."
        )
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "IBJA live metal rates are temporarily unavailable."
                ),
            },
            status=502,
        )
