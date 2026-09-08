from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
import nested_admin

from .models import (
    StoreLogoUpload,
    PinterestPost,
    Category,
    Product,
    ProductVariant,
    VariantStoreCoupon,
    HomeSlider,
    DropdownMenu,
    HomeSection,
    HomePageSEO,
    StoreConfiguration,
    submit_all_products_to_bing,
)


@admin.register(StoreLogoUpload)
class StoreLogoUploadAdmin(admin.ModelAdmin):
    list_display = ("id", "logo_path")


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


class VariantStoreCouponInline(nested_admin.NestedTabularInline):
    model = VariantStoreCoupon
    extra = 1


class ProductVariantInline(nested_admin.NestedStackedInline):
    model = ProductVariant
    inlines = [VariantStoreCouponInline]
    extra = 1
    classes = ("collapse",)


@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    list_display = (
        "title",
        "price_display",
        "category",
        "variant_thumbnail",
        "created_at",
    )
    list_filter = ("category", "currency")
    search_fields = ("title", "slug", "meta_keywords")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductVariantInline]
    actions = ["trigger_bing_submission"]

    def variant_thumbnail(self, obj):
        """Display the image of the first product variant in the admin list."""
        first_variant = obj.variants.first()
        if first_variant and first_variant.image_url:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                first_variant.image_url
            )
        return "No Image"

    variant_thumbnail.short_description = "Variant Image"

    @admin.action(description="Submit selected/all available products to Bing")
    def trigger_bing_submission(self, request, queryset):
        success = submit_all_products_to_bing()
        if success:
            self.message_user(request, "Successfully submitted products to Bing!")
        else:
            self.message_user(request, "Bing submission completed with some errors. Check logs.", level="WARNING")


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