
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import nested_admin
from import_export.admin import ImportExportModelAdmin
from .models import Category, Product, ProductVariant, HomeSlider, VariantStoreCoupon, DropdownMenu
from .indexing_utils import notify_google_indexing  # यहाँ फंक्शन को इम्पोर्ट करें



# --- 1. Nested Store Coupon Inline ---
class VariantStoreCouponInline(nested_admin.NestedTabularInline):
    model = VariantStoreCoupon
    extra = 0 # पहले से खाली रो नहीं आएगी, 'Add' बटन से जोड़ें
    fields = ('store_name', 'selling_price', 'coupon_code')
    # चौड़ाई कम करने के लिए कस्टम क्लास
    classes = []

# --- 2. Nested Product Variant Inline ---
class ProductVariantInline(nested_admin.NestedTabularInline):
    model = ProductVariant
    extra = 0
    readonly_fields = ('variant_code', 'image_url', 'display_image')
    # फील्ड्स को कॉम्पैक्ट रखा है
    fields = ('variant_code', 'image', 'display_image', 'earn_karo_url')
    inlines = [VariantStoreCouponInline]

    def display_image(self, obj):
        if obj and (obj.image_url or obj.image):
            img_src = obj.image_url if obj.image_url else obj.image.url
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain; border: 1px solid #ddd;" />', img_src)
        return "—"
    display_image.short_description = 'Preview'


# --- Action Function (Isse yahan paste karo) ---
@admin.action(description='Google Indexing: Notify Update')
def notify_google_indexing_action(modeladmin, request, queryset):
    count = 0
    for product in queryset:
        # Apni site ka sahi URL format yahan use karein
        url = f"https://uttarworld.com/product/{product.slug}/"
        try:
            # Yeh function indexing_utils.py se aa raha hai
            notify_google_indexing(url)
            count += 1
        except Exception as e:
            modeladmin.message_user(request, f"Error on {product.title}: {str(e)}", level=messages.ERROR)
    
    if count > 0:
        modeladmin.message_user(request, f"Successfully notified Google for {count} products!")

# --- 3. Main Product Admin ---
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, nested_admin.NestedModelAdmin):
   
    inlines = [ProductVariantInline]
    list_display = ('title', 'mrp_price', 'price_display', 'category', 'is_featured', 'is_available', 'main_image_preview')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    actions = [notify_google_indexing_action]

    fieldsets = (
        ('Basic Info', {'fields': ('title', 'slug', 'category')}),
        ('Pricing', {'fields': ('mrp_price', 'price_display')}),
        ('Descriptions', {'fields': ('long_description',)}),
        ('Status', {'fields': ('is_available', 'is_featured')}),
    )

    def main_image_preview(self, obj):
        first_variant = obj.variants.first()
        if first_variant and (first_variant.image_url or first_variant.image):
            img = first_variant.image_url if first_variant.image_url else first_variant.image.url
            return format_html('<img src="{}" width="40" height="40" />', img)
        return "—"

# --- 4. HomeSlider Admin ---
@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    fields = ('title', 'image', 'image_url', 'link', 'is_active')

# --- 5. Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    fields = ('name', 'slug', 'image', 'description', 'meta_keywords')
    prepopulated_fields = {'slug': ('name',)}

# --- 6. Dropdown Menu Manager Admin ---
@admin.register(DropdownMenu)
class DropdownMenuAdmin(admin.ModelAdmin):

    list_display = ['menu_name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('menu_name',)}