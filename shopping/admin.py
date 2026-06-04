from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import nested_admin  # ⚡ नेस्टेड एडमिन को इम्पोर्ट किया
from .models import Category, Product, ProductVariant, HomeSlider, VariantStoreCoupon, DropdownMenu

# --- 1. Nested Store Coupon Inline (सबसे अंदर का स्तर: कूपन और स्टोर्स) ---
class VariantStoreCouponInline(nested_admin.NestedTabularInline):
    model = VariantStoreCoupon
    extra = 1  # पहले से एक खाली रो दिखाई देगी एंट्री के लिए
    
    # 🎯 फ़िक्स: यहाँ से 'store_affiliate_url' को पूरी तरह हटा दिया गया है
    fields = ('store_name', 'selling_price', 'coupon_code', 'coupon_discount_value')
    classes = ['collapse']  # साफ-सुथरा दिखने के लिए इसे हाइड/शो करने का विकल्प दिया


# --- 2. Nested Product Variant Inline (बीच का स्तर: वेरिएंट जिसके अंदर कूपन भी होंगे) ---
class ProductVariantInline(nested_admin.NestedTabularInline):
    model = ProductVariant
    extra = 1
    
    # 🔒 'variant_code' और 'image_url', 'display_image' को रीड-ओनली रखा
    readonly_fields = ('variant_code', 'image_url', 'display_image')
    
    # कॉलम का क्रम
    fields = ('variant_code', 'image', 'display_image', 'earn_karo_url', 'image_url')
    
    # ⚡ जादुई जुड़वां: इस वेरिएंट के ठीक नीचे कूपन की रो खोलने के लिए
    inlines = [VariantStoreCouponInline]

    # 📸 लाइव इमेज प्रीव्यू फीचर (लोकल और लाइव यूआरएल दोनों के लिए फिक्स)
    def display_image(self, obj):
        if not obj or not obj.pk:
            return "—"
            
        if obj.image_url:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: contain; border: 2px solid #ddd; border-radius: 5px; background: #fff;" />', 
                obj.image_url
            )
        elif obj.image:
            try:
                return format_html(
                    '<img src="{}" width="60" height="60" style="object-fit: contain; border: 2px solid #ddd; border-radius: 5px; background: #fff;" />', 
                    obj.image.url
                )
            except ValueError:
                return mark_safe('<span style="color: #ff9800; font-weight: bold;">Processing...</span>')
            
        return mark_safe('<span style="color: #999;">No Image</span>')
        
    display_image.short_description = 'Live Preview'

    # एडमिन को साफ़ निर्देश देने के लिए
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if 'earn_karo_url' in formset.form.base_fields:
            formset.form.base_fields['earn_karo_url'].help_text = (
                "<strong style='color: #e42575; display: block; margin-top: 4px;'>"
                "⚠️ निर्देश: ऊपर दिख रहे कोड वाले कपड़े के लिए ही यहाँ सही EarnKaro/AJIO लिंक पेस्ट करें!</strong>"
            )
        return formset


# --- 3. Main Product Admin (मुख्य स्तर: जहाँ दोनों चीजें एक साथ दिखेंगी) ---
@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):  # ⚡ यहाँ NestedModelAdmin का उपयोग किया
    inlines = [ProductVariantInline]
    
    # लिस्ट व्यू में दिखने वाले कॉलम्स
    list_display = ('title', 'mrp_price', 'price_display', 'category', 'is_featured', 'is_available', 'main_image_preview')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('title', 'long_description')
    
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'category') 
        }),
        ('Pricing', {
            'fields': ('mrp_price', 'price_display'), # ⚡ यहाँ fixed MRP का बॉक्स जोड़ दिया है
            'description': "<span style='color: #1e3c72;'><strong>💡 नोट:</strong> MRP यहाँ स्थिर रहेगा। वेरिएंट के अंदर सेलिंग प्राइस डालते ही डिस्काउंट खुद कैलकुलेट हो जाएगा।</span>"
        }),
        ('Descriptions', {
            'fields': ('long_description',)
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured')
        }),
    )

    # 📸 मुख्य लिस्ट में पहले वेरिएंट का प्रीव्यू दिखाने का एकदम सुरक्षित जुगाड़
    def main_image_preview(self, obj):
        if not obj.pk:
            return "—"
            
        first_variant = obj.variants.first() if hasattr(obj, 'variants') else None
        
        if first_variant:
            if getattr(first_variant, 'image_url', None):
                return format_html(
                    '<img src="{}" width="40" height="40" style="object-fit: contain; border-radius: 4px; background: #fff; border: 1px solid #eee;" />', 
                    first_variant.image_url
                )
            elif getattr(first_variant, 'image', None) and first_variant.image:
                try:
                    return format_html(
                        '<img src="{}" width="40" height="40" style="object-fit: contain; border-radius: 4px; background: #fff; border: 1px solid #eee;" />', 
                        first_variant.image.url
                    )
                except ValueError:
                    return "—"
        return "—"
        
    main_image_preview.short_description = 'Image'


# --- 4. HomeSlider Admin ---
@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'thumbnail')
    fields = ('title', 'image', 'image_url', 'link', 'is_active')
    readonly_fields = ('image_url',)

    def thumbnail(self, obj):
        if obj and obj.image_url:
            return format_html('<img src="{}" width="100" style="border-radius: 8px; border: 1px solid #ccc;" />', obj.image_url)
        elif obj and obj.image:
            try:
                return format_html('<img src="{}" width="100" style="border-radius: 8px; border: 1px solid #ccc;" />', obj.image.url)
            except ValueError:
                pass
        return "No Image"
    thumbnail.short_description = 'Preview'


# --- 5. Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category_icon')
    
    # Yahan description aur meta_keywords add kar diye hain
    fields = ('name', 'slug', 'image', 'image_url', 'description', 'meta_keywords')
    
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_url',)

    def category_icon(self, obj):
        if obj and obj.image_url:
            return format_html('<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%; background: #f0f0f0;" />', obj.image_url)
        elif obj and obj.image:
            try:
                return format_html('<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%; background: #f0f0f0;" />', obj.image.url)
            except ValueError:
                pass
        return "No Icon"
    category_icon.short_description = 'Icon'
    
# --- 6. Dropdown Menu Manager Admin 🚀 ---
@admin.register(DropdownMenu)
class DropdownMenuAdmin(admin.ModelAdmin):
    list_display = ['menu_name', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']  # एडमिन लिस्ट से ही ऑन/ऑफ या आर्डर बदल सकते हैं
    prepopulated_fields = {'slug': ('menu_name',)}
    
    # 🎯 इससे एडमिन पैनल में कैट