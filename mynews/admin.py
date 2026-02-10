from django.contrib import admin
from django.db import models 
from .models import News
from django.utils.html import format_html
import gc

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('display_thumb', 'title', 'district', 'status', 'share_now_to_fb', 'date')
    list_filter = ('status', 'district', 'category', 'date', 'share_now_to_fb')
    search_fields = ('title', 'content')
    list_editable = ('status', 'share_now_to_fb')
    readonly_fields = ('image_url', 'is_fb_posted', 'display_large_img')
    fieldsets = (
        ('News Content', {'fields': ('title', 'status', 'content'),}),
        ('Location & Category', {'fields': (('district', 'category', 'url_city'),),}),
        ('Media', {'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url'),}),
        ('Settings', {'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted')),}),
        ('SEO', {'fields': ('slug', 'date', 'meta_keywords'), 'classes': ('collapse',),}),
    )

    def display_thumb(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image_url)
        return "No Pic"

    def display_large_img(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-width: 300px; border-radius: 10px;" />', obj.image_url)
        return "No Preview"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        gc.collect()
