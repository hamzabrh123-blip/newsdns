
from django.contrib import admin, messages
from django.utils.html import format_html

import nested_admin

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from .models import (
    Category,
    Product,
    ProductVariant,
    HomeSlider,
    VariantStoreCoupon,
    DropdownMenu,
    HomeSection,
)

from .indexing_utils import notify_google_indexing


# =========================================================
# IMPORT EXPORT RESOURCES
# =========================================================

class ProductResource(resources.ModelResource):

    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'pk')
    )

    class Meta:

        model = Product

        fields = (
            'id',
            'title',
            'slug',
            'category',
            'mrp_price',
            'price_display',
        )

        import_id_fields = ('id',)


# =========================================================
# INLINE: COUPONS
# =========================================================

class VariantStoreCouponInline(
    nested_admin.NestedTabularInline
):

    model = VariantStoreCoupon

    extra = 0

    fields = (
        'store_name',
        'selling_price',
        'coupon_code',
    )


# =========================================================
# INLINE: PRODUCT VARIANTS
# =========================================================

class ProductVariantInline(
    nested_admin.NestedTabularInline
):

    model = ProductVariant

    extra = 0

    readonly_fields = (
        'variant_code',
        'display_image',
    )

    fields = (
        'variant_code',
        'image',
        'display_image',
        'earn_karo_url',
    )

    inlines = [VariantStoreCouponInline]

    def display_image(self, obj):

        if obj and (obj.image_url or obj.image):

            image_src = (
                obj.image_url
                if obj.image_url
                else obj.image.url
            )

            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit:contain;" />',
                image_src
            )

        return "—"

    display_image.short_description = "Preview"


# =========================================================
# GOOGLE INDEXING ACTION
# =========================================================

@admin.action(description='Notify Google Indexing')
def notify_google_indexing_action(
    modeladmin,
    request,
    queryset
):

    success_count = 0

    for obj in queryset:

        if hasattr(obj, 'slug'):

            try:

                if modeladmin.model.__name__ == 'Category':

                    url = (
                        f"https://uttarworld.com/category/{obj.slug}/"
                    )

                else:

                    url = (
                        f"https://uttarworld.com/product/{obj.slug}/"
                    )

                notify_google_indexing(url)

                success_count += 1

            except Exception as e:

                modeladmin.message_user(
                    request,
                    f"Error on {obj}: {str(e)}",
                    level=messages.ERROR
                )

    if success_count > 0:

        modeladmin.message_user(
            request,
            f"Successfully notified for {success_count} items!"
        )


# =========================================================
# HOME SECTION ADMIN
# =========================================================

# =========================================================
# HOME SECTION ADMIN
# =========================================================

@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):

    list_display = (
        'category',
        'order',
        'is_active',
    )

    list_editable = (
        'order',
        'is_active',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'category__name',
    )

    readonly_fields = (
        'section_image_preview',
    )

    fields = (
        'image',
        'section_image_preview',
        'category',
        'order',
        'is_active',
    )

    def section_image_preview(self, obj):

        if obj.image:

            return format_html(
                '<img src="{}" width="120" style="border-radius:8px;" />',
                obj.image.url
            )

        return "No Image"

    section_image_preview.short_description = "Preview"

# =========================================================
# PRODUCT ADMIN
# =========================================================

@admin.register(Product)
class ProductAdmin(
    ImportExportModelAdmin,
    nested_admin.NestedModelAdmin
):

    resource_class = ProductResource

    inlines = [ProductVariantInline]

    list_display = (
        'title',
        'mrp_price',
        'price_display',
        'category',
        'is_featured',
        'is_available',
        'main_image_preview',
    )

    list_filter = (
        'category',
        'is_available',
        'is_featured',
    )

    list_editable = (
        'is_featured',
        'is_available',
    )

    search_fields = (
        'title',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    actions = [
        notify_google_indexing_action
    ]

    fieldsets = (

        (
            'Basic Information',
            {
                'fields': (
                    'title',
                    'slug',
                    'category',
                    'mrp_price',
                    'price_display',
                )
            }
        ),

        (
            'SEO Settings',
            {
                'fields': (
                    'meta_description',
                    'meta_keywords',
                )
            }
        ),

        (
            'Content',
            {
                'fields': (
                    'long_description',
                )
            }
        ),

        (
            'Status',
            {
                'fields': (
                    'is_available',
                    'is_featured',
                )
            }
        ),

    )

    def main_image_preview(self, obj):

        first_variant = obj.variants.first()

        if first_variant and (
            first_variant.image_url or first_variant.image
        ):

            image_src = (
                first_variant.image_url
                if first_variant.image_url
                else first_variant.image.url
            )

            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:contain;" />',
                image_src
            )

        return "—"

    main_image_preview.short_description = "Preview"


# =========================================================
# HOME SLIDER ADMIN
# =========================================================

@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'is_active',
    )


# =========================================================
# CATEGORY ADMIN
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'category_image_preview',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    actions = [
        notify_google_indexing_action
    ]

    def category_image_preview(self, obj):

        if obj.image_url:

            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:4px;" />',
                obj.image_url
            )

        if obj.image:

            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit:cover;border-radius:4px;" />',
                obj.image.url
            )

        return "No Image"

    category_image_preview.short_description = "Preview"


# =========================================================
# DROPDOWN MENU ADMIN
# =========================================================

@admin.register(DropdownMenu)
class DropdownMenuAdmin(admin.ModelAdmin):

    list_display = (
        'menu_name',
        'order',
        'is_active',
    )

    list_editable = (
        'order',
        'is_active',
    )

    prepopulated_fields = {
        'slug': ('menu_name',)
    }


# =========================================================
# HIDE UNUSED MODELS FROM SIDEBAR
# =========================================================

try:
    admin.site.unregister(ProductVariant)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(VariantStoreCoupon)
except admin.sites.NotRegistered:
    pass

