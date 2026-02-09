from django.contrib import admin
from django.db import models 
from .models import News
from django.utils.html import format_html
import gc

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    # 1. Bahar ki list me ab thumbnail dikhega
    list_display = ('display_thumb', 'title', 'district', 'status', 'share_now_to_fb', 'is_fb_posted', 'date')
    
    # 2. Side filters
    list_filter = ('status', 'district', 'category', 'date', 'is_important', 'show_in_highlights', 'share_now_to_fb')
    
    # 3. Search Bar
    search_fields = ('title', 'content')
    
    # 4. Direct edit from list
    list_editable = ('status', 'share_now_to_fb')
    
    list_per_page = 20
    
    # System generated fields (Read-only)
    readonly_fields = ('category', 'url_city', 'image_url', 'is_fb_posted', 'display_large_img')

    # UI Design for Title box
    formfield_overrides = {
        models.CharField: {
            'widget': admin.widgets.AdminTextInputWidget(
                attrs={
                    'style': 'width: 100%; padding: 12px; font-size: 1.1rem; border: 2px solid #b91d1d; border-radius: 5px;'
                }
            )
        },
    }

    # Layout Sections
    fieldsets = (
        ('Main Info', {
            'fields': ('title', 'status', 'content'),
        }),
        ('Location', {
            'fields': (('district', 'category', 'url_city'),),
        }),
        ('Media', {
            'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url'),
        }),
        ('Social & Highlights', {
            'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted')),
        }),
        ('SEO', {
            'fields': ('slug', 'date', 'meta_keywords'), 
            'classes': ('collapse',),
        }),
    )

    # Functions to show images
    def display_thumb(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image_url)
        return "No Pic"
    display_thumb.short_description = "Pic"

    def display_large_img(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-width: 300px; border: 2px solid #b91d1d; border-radius: 10px;" />', obj.image_url)
        return "No Preview"
    display_large_img.short_description = "Live Preview"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        gc.collect()

admin.site.site_header = "Uttar World Administration"
admin.site.index_title = "Welcome to News Dashboard"
