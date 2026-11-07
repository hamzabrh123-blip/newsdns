import time
import requests
from django.contrib import admin, messages
from django.conf import settings
from .models import Product
from .pin_models import PinterestBoard, PinterestPost

@admin.register(PinterestBoard)
class PinterestBoardAdmin(admin.ModelAdmin):
    list_display = ("name", "board_id", "created_at")
    search_fields = ("name", "board_id")


@admin.register(PinterestPost)
class PinterestPostAdmin(admin.ModelAdmin):
    list_display = ("title", "board", "is_published", "created_at")
    list_filter = ("is_published", "board")
    search_fields = ("title", "link")


@admin.action(description="Selected products ko Pinterest par Push karein (Max 50)")
def bulk_push_to_pinterest(modeladmin, request, queryset):
    token = getattr(settings, "PINTEREST_ACCESS_TOKEN", "")
    if not token:
        messages.error(request, "PINTEREST_ACCESS_TOKEN Render environment variables me missing hai!")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    batch_products = queryset[:50]
    success_count = 0
    failed_count = 0

    for product in batch_products:
        if not product.pinterest_board:
            failed_count += 1
            continue
            
        product_url = f"https://uttarworld.com/product/{product.slug}/"
        
        image_url = ""
        if hasattr(product, 'image') and product.image:
            image_url = product.image.url if hasattr(product.image, 'url') else str(product.image)
        elif product.variants.exists():
            first_variant = product.variants.first()
            image_url = first_variant.image_url or ""

        if not image_url:
            failed_count += 1
            continue

        payload = {
            "board_id": product.pinterest_board.board_id,
            "title": product.title[:100],
            "description": product.meta_description[:500] if product.meta_description else product.title,
            "link": product_url,
            "media_source": {
                "source_type": "image_url",
                "url": image_url
            }
        }

        try:
            response = requests.post("https://api.pinterest.com/v5/pins", json=payload, headers=headers, timeout=10)
            if response.status_code == 201:
                success_count += 1
                PinterestPost.objects.create(
                    title=product.title,
                    image_url=image_url,
                    link=product_url,
                    board=product.pinterest_board,
                    is_published=True
                )
            else:
                failed_count += 1
        except Exception:
            failed_count += 1

        time.sleep(0.2)

    messages.success(
        request, 
        f"Pinterest Batch Complete: {success_count} Pins successfully publish hue. ({failed_count} skipped/failed)"
    )