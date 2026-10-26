import json
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import FSJJewellery


@csrf_exempt
@require_POST
def create_jewellery(request):
    name = request.POST.get("name", "").strip()
    category = request.POST.get("category", "Ring")
    purity = request.POST.get("purity", "22K")
    description = request.POST.get("description", "").strip()
    image = request.FILES.get("image")

    if not name or not image:
        return JsonResponse(
            {"success": False, "error": "Name and image are required"},
            status=400,
        )

    try:
        weight = Decimal(request.POST.get("weight_grams", "0"))
        price = Decimal(request.POST.get("price", "0"))
        if weight <= 0 or price < 0:
            raise InvalidOperation
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse(
            {"success": False, "error": "Invalid weight or price"},
            status=400,
        )

    item = FSJJewellery.objects.create(
        name=name,
        category=category,
        purity=purity,
        weight_grams=weight,
        price=price,
        description=description,
        image=image,
    )

    return JsonResponse({
        "success": True,
        "id": item.id,
        "name": item.name,
        "image_url": item.image.url,
    }, status=201)