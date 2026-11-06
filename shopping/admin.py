from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.html import format_html
from django.conf import settings
from import_export.admin import ImportExportModelAdmin
import requests
import time

from .indexing_utils import notify_google_indexing
from .models import ping_bing_indexing_batch, ShopNowClick
from .models import (
    StoreLogoUpload,
    PinterestPost,
    Category,
    Product,
    ProductVariant,
    HomeSlider,
    DropdownMenu,
    HomeSection,
    HomePageSEO,
    StoreConfiguration,
)


@admin.register(StoreLogoUpload)
class StoreLogoUploadAdmin(admin.ModelAdmin):
    list_display = ("id", "logo_path")

    def has_module_permission(self, request):
        return False


@admin.register(PinterestPost)
class PinterestPostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "link")


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ("name", "slug", "meta_title")
    search_fields = ("name", "meta_title")
    prepopulated_fields = {"slug": ("name",)}
    actions = ["trigger_google_category_submission", "trigger_bing_category_submission"]

    @admin.action(description="Submit selected categories to Google")
    def trigger_google_category_submission(self, request, queryset):
        urls = [f"https://uttarworld.com{cat.get_absolute_url()}" for cat in queryset if cat.slug]
        success, failed = 0, 0
        for url in urls:
            try:
                result = notify_google_indexing(url)
                if isinstance(result, dict) and result.get("status") == "success":
                    success += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        self.message_user(request, f"Google category submission: {success} successful, {failed} failed.")

    @admin.action(description="Submit selected categories to Bing")
    def trigger_bing_category_submission(self, request, queryset):
        urls = [f"https://uttarworld.com{cat.get_absolute_url()}" for cat in queryset if cat.slug]
        success = ping_bing_indexing_batch(urls)
        if success:
            self.message_user(request, f"Bing submission successful for {len(urls)} categories.")
        else:
            self.message_user(request, "Bing submission failed or was incomplete.", level="WARNING")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "variant_image_preview", 
        "image_url", 
        "video_url", 
        "earn_karo_url", 
        "selling_price", 
        "size", 
        "colour", 
        "mrp_price"
    )
    readonly_fields = ("variant_image_preview",)

    formfield_overrides = {
        models.URLField: {"widget": TextInput(attrs={"size": 15, "style": "width: 120px;"})},
        models.CharField: {"widget": TextInput(attrs={"size": 10, "style": "width: 85px;"})},
        models.DecimalField: {"widget": TextInput(attrs={"size": 8, "style": "width: 75px;"})},
    }

    class Media:
        css = {
            'all': (
                'data:text/css;charset=utf-8,'
                '.inline-group .tabular td { padding: 6px 3px !important; } '
                '.inline-group .tabular input { max-width: 130px !important; box-sizing: border-box; }'
            ),
        }

    def variant_image_preview(self, obj):
        if obj and obj.image_url:
            return format_html(
                '<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />',
                obj.image_url
            )
        return "No Image"
    variant_image_preview.short_description = "Preview"


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = (
        "title",
        "display_store_name",
        "display_selling_price",
        "category",
        "variant_thumbnail",
        "created_at",
    )
    list_filter = ("category", "store_name", "currency")
    search_fields = ("title", "slug", "meta_keywords", "store_name")
    
    exclude = ("slug",)
    readonly_fields = ("product_image_preview",)
    
    fields = (
        "title",
        "category",
        "store_name",
        "mrp_price",
        "selling_price",
        "default_color",
        "default_size",
        "currency",
        "product_image_preview",
        "long_description",
        "meta_description",
        "meta_keywords",
        "is_available",
        "is_featured",
    )
    
    inlines = [ProductVariantInline]
    actions = ["trigger_google_submission", "trigger_bing_submission", "trigger_pinterest_submission"] 
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 3})},
    }

    def display_store_name(self, obj):
        return obj.store_name if obj.store_name else "-"
    display_store_name.short_description = "Store Name"

    def display_selling_price(self, obj):
        if obj.selling_price and obj.selling_price > 0:
            return f"{obj.currency} {obj.selling_price}"
        if obj.mrp_price and obj.mrp_price > 0:
            return f"{obj.currency} {obj.mrp_price} (MRP)"
        return f"{obj.currency} - "
    display_selling_price.short_description = "Selling Price"

    def variant_thumbnail(self, obj):
        first_variant = obj.variants.first()
        if first_variant and first_variant.image_url:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                first_variant.image_url
            )
        return "No Image"
    variant_thumbnail.short_description = "Variant Image"

    def product_image_preview(self, obj):
        if obj and obj.pk:
            first_variant = obj.variants.first()
            if first_variant and first_variant.image_url:
                return format_html(
                    '<img src="{}" style="max-height: 150px; max-width: 150px; object-fit: cover; border-radius: 6px;" />',
                    first_variant.image_url
                )
        return "Save product once or add variant image to preview here."
    product_image_preview.short_description = "Product Main Image Preview"

    @admin.action(description="Submit selected products to Google")
    def trigger_google_submission(self, request, queryset):
        urls = [
            f"https://uttarworld.com/shopping/product/{p.slug}/"
            for p in queryset.filter(is_available=True)
            .exclude(slug__isnull=True)
            .exclude(slug="")
        ]

        success = 0
        failed = 0
        errors = []

        for url in urls:
            try:
                result = notify_google_indexing(url)
                if isinstance(result, dict) and result.get("status") == "success":
                    success += 1
                else:
                    failed += 1
                    if len(errors) < 3:
                        errors.append(f"{url}: {result!r}")
            except Exception as e:
                failed += 1
                if len(errors) < 3:
                    errors.append(f"{url}: {type(e).__name__}: {e}")

        self.message_user(request, f"Google submission: {success} successful, {failed} failed.")
        for error in errors:
            self.message_user(request, error[:1000], level="WARNING")

    @admin.action(description="Submit selected products to Bing")
    def trigger_bing_submission(self, request, queryset):
        urls = [
            f"https://uttarworld.com/shopping/product/{p.slug}/"
            for p in queryset.filter(is_available=True)
            .exclude(slug__isnull=True)
            .exclude(slug="")
        ]

        success = ping_bing_indexing_batch(urls)

        if success:
            self.message_user(request, f"Bing submission successful for {len(urls)} URLs.")
        else:
            self.message_user(request, "Bing submission failed or was incomplete. Check logs.", level="WARNING")

    @admin.action(description="Submit selected products to Pinterest (Bulk Up to 100)")
    def trigger_pinterest_submission(self, request, queryset):
        access_token = getattr(settings, "PINTEREST_ACCESS_TOKEN", "")
        board_id = getattr(settings, "PINTEREST_BOARD_ID", "")

        if not access_token or not board_id:
            self.message_user(request, "Pinterest Access Token or Board ID not configured in settings.", level="ERROR")
            return

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        products_to_pin = queryset.filter(is_available=True).exclude(slug__isnull=True).exclude(slug="")[:100]
        
        success_count = 0
        fail_count = 0

        for product in products_to_pin:
            first_variant = product.variants.first()
            image_url = first_variant.image_url if first_variant and first_variant.image_url else ""
            
            if not image_url:
                fail_count += 1
                continue

            payload = {
                "board_id": board_id,
                "title": product.title[:100],
                "description": (product.long_description or product.meta_description or product.title)[:500],
                "link": f"https://uttarworld.com/shopping/product/{product.slug}/",
                "media_source": {
                    "source_type": "image_url",
                    "url": image_url
                }
            }

            try:
                response = requests.post("https://api.pinterest.com/v5/pins", json=payload, headers=headers, timeout=10)
                if response.status_code == 201:
                    success_count += 1
                else:
                    fail_count += 1
                time.sleep(1)
            except Exception:
                fail_count += 1

        self.message_user(
            request,
            f"Pinterest bulk push finished: {success_count} pins created successfully, {fail_count} failed/skipped."
        )


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ("title", "link", "is_active")
    list_filter = ("is_active",)


@admin.register(DropdownMenu)
class DropdownMenuAdmin(admin.ModelAdmin):
    list_display = ("menu_name", "order", "is_active")
    list_filter = ("is_active",)
    filter_horizontal = ("categories",)


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order", "is_active")
    list_filter = ("is_active", "category")
    list_editable = ("order", "is_active")


@admin.register(HomePageSEO)
class HomePageSEOAdmin(admin.ModelAdmin):
    list_display = ("title", "updated_at")


@admin.register(StoreConfiguration)
class StoreConfigurationAdmin(admin.ModelAdmin):
    list_display = ("store_name", "default_coupon_code", "is_active")
    list_filter = ("is_active",)

    def has_module_permission(self, request):
        return False


@admin.register(ShopNowClick)
class ShopNowClickAdmin(admin.ModelAdmin):
    list_display = (
        "clicked_at",
        "product",
        "variant",
        "store_name",
        "city",
        "country",
    )
    list_filter = ("store_name", "country", "clicked_at")
    search_fields = (
        "product__title",
        "store_name",
        "city",
        "country",
        "variant__variant_code",
    )
    ordering = ("-clicked_at",)
    readonly_fields = ("clicked_at",)