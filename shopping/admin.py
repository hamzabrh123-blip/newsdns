from django.contrib import admin
from .models import Category, Product, ProductImage, HomeSlider

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    # यहाँ 'image' सिर्फ अपलोड के लिए है, असली चीज़ 'image_url' है
    fields = ('image', 'image_url') 
    # readonly_fields का मतलब है कि यहाँ ImgBB का लिंक दिखेगा
    readonly_fields = ('image_url',)

# --- 2. Product Admin ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline] # गैलरी जोड़ दी
    
    # list_display में से 'old_price' हटा दिया गया है
    list_display = ('title', 'price', 'category', 'is_featured', 'is_available')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    
    # Fieldsets को मॉडल्स के हिसाब से अपडेट किया गया है
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'category', 'buy_now_url') 
        }),
        ('Pricing', {
            'fields': ('price',) # यहाँ सिर्फ price रखा है, old_price हटा दिया
        }),
        ('Descriptions', {
            'fields': ('short_description', 'long_description')
        }),
        # 'Main Media' सेक्शन हटा दिया क्योंकि अब हम Gallery (ProductImage) यूज़ कर रहे हैं
        ('Status', {
            'fields': ('is_available', 'is_featured')
        }),
    )

# --- 3. HomeSlider Admin ---
@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    readonly_fields = ('image_url',)

# --- 4. Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_url',)