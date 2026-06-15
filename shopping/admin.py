from django.contrib import admin, messages
from django.utils.html import format_html
import nested_admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import (
    Category, Product, ProductVariant, HomeSlider, 
    VariantStoreCoupon, DropdownMenu
)
from .indexing_utils import notify_google_indexing

# --- Resources ---
class ProductResource(resources.ModelResource):
    category = fields.Field(column_name='category', attribute='category', widget=ForeignKeyWidget(Category, 'pk'))
    class Meta:
        model = Product
        fields = ('id', 'title', 'slug', 'category', 'mrp_price', 'price_display')
        import_id_fields = ('id',)

class ProductVariantResource(resources.ModelResource):
    product = fields.Field(column_name='product', attribute='product', widget=ForeignKeyWidget(Product, 'title'))
    class Meta:
        model = ProductVariant
        fields = ('id', 'product', 'variant_code', 'earn_karo_url')
        import_id_fields = ('id',)

class VariantStoreCouponResource(resources.ModelResource):
    variant_code = fields.Field(column_name='variant_code', attribute='variant', widget=ForeignKeyWidget(ProductVariant, 'variant_code'))
    class Meta:
        model = VariantStoreCoupon
        fields = ('id', 'variant_code', 'store_name', 'selling_price', 'coupon_code')
        import_id_fields = ('id',)

# --- Inlines ---
class VariantStoreCouponInline(nested_admin.NestedTabularInline):
    model = VariantStoreCoupon
    extra = 0
    fields = ('store_name', 'selling_price', 'coupon_code')

class ProductVariantInline(nested_admin.NestedTabularInline):
    model = ProductVariant
    extra = 0
    readonly_fields = ('variant_code', 'display_image')
    fields = ('variant_code', 'image', 'display_image', 'earn_karo_url')
    inlines = [VariantStoreCouponInline]

    def display_image(self, obj):
        if obj and (obj.image_url or obj.image):
            img_src = obj.image_url if obj.image_url else obj.image.url
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;" />', img_src)
        return "—"

# --- Actions ---
@admin.action(description='Google Indexing: Notify Update')
def notify_google_indexing_action(modeladmin, request, queryset):
    count = 0
    for product in queryset:
        url = f"https://uttarworld.com/product/{product.slug}/"
        try:
            notify_google_indexing(url)
            count += 1
        except Exception as e:
            modeladmin.message_user(request, f"Error: {str(e)}", level=messages.ERROR)
    if count > 0:
        modeladmin.message_user(request, f"Successfully notified for {count} products!")

# --- Registrations ---
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
    resource_class = ProductResource
    inlines = [ProductVariantInline]
    list_display = ('title', 'mrp_price', 'category', 'is_featured', 'is_available', 'main_image_preview')
    list_filter = ('category', 'is_available', 'is_featured')
    list_editable = ('is_featured', 'is_available')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    actions = [notify_google_indexing_action]

    def main_image_preview(self, obj):
        first_variant = obj.variants.first()
        if first_variant and (first_variant.image_url or first_variant.image):
            img = first_variant.image_url if first_variant.image_url else first_variant.image.url
            return format_html('<img src="{}" width="40" height="40" />', img)
        return "—"

@admin.register(ProductVariant)
class ProductVariantAdmin(ImportExportModelAdmin):
    resource_class = ProductVariantResource
    list_display = ('variant_code', 'product', 'earn_karo_url')
    search_fields = ('variant_code', 'product__title')

@admin.register(VariantStoreCoupon)
class VariantStoreCouponAdmin(ImportExportModelAdmin):
    resource_class = VariantStoreCouponResource
    list_display = ('variant', 'store_name', 'selling_price', 'coupon_code')
    list_editable = ('selling_price', 'coupon_code')
    search_fields = ('variant__variant_code', 'store_name')

@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DropdownMenu)
class DropdownMenuAdmin(admin.ModelAdmin):
    list_display = ['menu_name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('menu_name',)}