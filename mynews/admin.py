from django.contrib import admin
from .models import News
from .constants import LOCATION_DATA
from django.utils.html import format_html
import gc

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    # 1. List View: News list mein kya-kya dikhega
    list_display = ('display_thumb', 'title', 'district', 'category', 'status', 'date')
    list_filter = ('status', 'district', 'category', 'date')
    search_fields = ('title', 'content')
    
    # List se hi status aur district badalne ki suvidha
    list_editable = ('status', 'district') 

    # 2. Readonly Fields: Inhe Django ka backend (models.py) khud bharega
    # Inhe readonly rakhne se EDIT karte waqt kabhi error nahi aayega
    readonly_fields = ('image_url', 'is_fb_posted', 'display_large_img', 'category', 'url_city')

    # 3. Fieldsets: Admin panel ka layout
    fieldsets = (
        ('News Content', {
            'fields': ('title', 'status', 'content'),
        }),
        ('Location & Category (Auto-Set)', {
            'fields': (('district', 'category', 'url_city'),),
            'description': 'Sirf District/Category dropdown chuno, baaki dono apne aap bhar jayenge.',
        }),
        ('Media Section', {
            'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url'),
        }),
        ('Automation & Highlights', {
            'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted')),
        }),
        ('SEO & Metadata', {
            'fields': ('slug', 'date', 'meta_keywords'),
            'classes': ('collapse',), # Isse SEO wala dabba hide rahega, click karne par khulega
        }),
    )

    # 4. Thumbnail Display Logic (Chhoti Photo list mein)
    def display_thumb(self, obj):
        # Priority: Pehle ImgBB ka link, fir local image
        img_src = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_src:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', img_src)
        return "No Pic"
    display_thumb.short_description = "Preview"

    # 5. Large Image Preview (Badi photo detail page mein)
    def display_large_img(self, obj):
        img_src = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_src:
            return format_html('<img src="{}" style="max-width: 300px; border-radius: 10px;" />', img_src)
        return "No Preview"
    display_large_img.short_description = "Large Preview"

    # 6. Save Logic (Memory cleaning)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        gc.collect() # Server ki memory free karne ke liye
