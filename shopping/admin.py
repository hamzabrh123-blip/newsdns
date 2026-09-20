from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

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
    submit_all_products_to_bing,
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

    def has_module_permission(self, request):
        return False


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ("name", "slug", "meta_title")
    search_fields = ("name", "meta_title")
    prepopulated_fields = {"slug": ("name",)}


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("variant_image_preview", "image_url", "earn_karo_url", "selling_price", "colour", "video_url")
    readonly_fields = ("variant_image_preview",)

    # Widget ko explicitly TextInput se replace kiya hai taaki 'फिलहाल' hamesha ke liye gayab ho jaye
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'image_url':
            field.widget = TextInput(attrs={'style': 'width: 310px;' 'display: inline-block;'})
        elif db_field.name == 'earn_karo_url':
            field.widget = TextInput(attrs={'style': 'width: 210px;'})
        elif db_field.name == 'selling_price':
            field.widget.attrs['style'] = 'width: 90px;'
        elif db_field.name == 'colour':
            field.widget.attrs['style'] = 'width: 100px;'
        elif db_field.name == 'video_url':
            field.widget.attrs['style'] = 'width: 110px;'
        return field

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
        "video_url",
        "currency",
        "product_image_preview",
        "long_description",
        "meta_description",
        "meta_keywords",
        "is_available",
        "is_featured",
    )
    
    inlines = [ProductVariantInline]
    actions = ["trigger_bing_submission"]

    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 3})},
    }

    class Media:
        css = {
            "all": ("admin/css/custom_admin.css",)
        }

    def display_store_name(self, obj):
        return obj.store_name if obj.store_name else "-"
    display_store_name.short_description = "Store Name"

    def display_selling_price(self, obj):
        if obj.selling_price and obj.selling_price > 0:
            return f"{obj.currency} {obj.selling_price}"
        return f"{obj.currency} {obj.mrp_price} (MRP)"
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

    @admin.action(description="Submit selected/all available products to search engines")
    def trigger_bing_submission(self, request, queryset):
        success = submit_all_products_to_bing()
        if success:
            self.message_user(request, "Successfully submitted products to search engines!")
        else:
            self.message_user(request, "Submission completed with some errors. Check logs.", level="WARNING")


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