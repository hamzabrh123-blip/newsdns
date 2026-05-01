from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, HomeSlider, ProductLink

# --- 1. Product Link Inline (Unlimited Buttons) ---
class ProductLinkInline(admin.TabularInline):
    model = ProductLink
    extra = 1

# --- 2. Product Image Inline (Gallery) ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'display_image', 'image_url') 
    readonly_fields = ('image_url', 'display_image')

    def display_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border: 2px solid #ddd; border-radius: 5px;" />', obj.image_url)
        elif obj.image:
            return "Processing..."
        return "No Image"
    display_image.short_description = 'Live Preview'

# --- 3. Product Admin ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # अब इसमें ProductLink भी जोड़ दिया है
    inlines = [ProductLinkInline, ProductImageInline]
    
    # 'price' को 'price_display' से बदला
    list_display = ('title', 'price_display', 'category', 'is_featured', 'is_available', 'main_image_preview')
    list_filter = ('category', 'is_available', 'is_featured')
    
    # 'short_description' हटाकर सर्च को सिर्फ title और long_description पर रखा
    search_fields = ('title', 'long_description')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'category') 
        }),
        ('Pricing', {
            # यहाँ भी 'price_display' किया
            'fields': ('price_display',)
        }),
        ('Descriptions', {
            # 'short_description' हटा दिया
            'fields': ('long_description',)
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured')
        }),
    )

    def main_image_preview(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image_url:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 4px;" />', first_image.image_url)
        return "—"
    main_image_preview.short_description = 'Image'

# --- 4. HomeSlider Admin ---
@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'thumbnail')
    fields = ('title', 'image', 'image_url', 'link', 'is_active')
    readonly_fields = ('image_url',)

    def thumbnail(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="100" style="border-radius: 8px; border: 1px solid #ccc;" />', obj.image_url)
        return "No Image"
    thumbnail.short_description = 'Preview'

# --- 5. Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category_icon')
    fields = ('name', 'slug', 'image', 'image_url')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_url',)

    def category_icon(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%; background: #f0f0f0;" />', obj.image_url)
        return "No Icon"
    category_icon.short_description = 'Icon'