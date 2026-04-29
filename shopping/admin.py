from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, HomeSlider

# --- 1. Product Image Inline (Gallery) ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    # 'image' अपलोड के लिए, 'display_image' प्रीव्यू के लिए
    fields = ('image', 'display_image', 'image_url') 
    readonly_fields = ('image_url', 'display_image')

    def display_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image_url)
        return "No Image"
    display_image.short_description = 'Preview'

# --- 2. Product Admin ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('title', 'price', 'category', 'is_featured', 'is_available')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'category', 'buy_now_url') 
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Descriptions', {
            'fields': ('short_description', 'long_description')
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured')
        }),
    )

# --- 3. HomeSlider Admin ---
@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'thumbnail')
    readonly_fields = ('image_url',)

    def thumbnail(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="100" style="border-radius: 5px;" />', obj.image_url)
        return "No Image"

# --- 4. Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category_icon')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_url',)

    def category_icon(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%;" />', obj.image_url)
        return "No Icon"
