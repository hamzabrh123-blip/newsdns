from django.contrib import admin
from .models import Category, Product, ProductImage, HomeSlider

# गैलरी के लिए इनलाइन सेटअप (ताकि प्रोडक्ट पेज पर ही 5 फोटो के डब्बे दिखें)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5 
    fields = ['image', 'alt_text']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline] # गैलरी जोड़ दी
    list_display = ('title', 'price', 'category', 'is_featured', 'is_available')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    
    # यहाँ ध्यान दे: मैंने 'buy_now_url' को 'Basic Info' में जोड़ दिया है
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'category', 'buy_now_url') 
        }),
        ('Pricing', {
            'fields': ('old_price', 'price')
        }),
        ('Descriptions', {
            'fields': ('short_description', 'long_description')
        }),
        ('Main Media', {
            'fields': ('main_image',)
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured')
        }),
    )

# कैटेगरी को अलग से रजिस्टर किया
admin.site.register(Category)
admin.site.register(HomeSlider)