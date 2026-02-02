from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'category', 'date', 'is_important', 'share_now_to_fb', 'is_fb_posted')
    list_filter = ('district', 'category', 'date', 'is_important', 'is_fb_posted')
    search_fields = ('title', 'content')
    list_editable = ('is_important', 'share_now_to_fb')
    list_per_page = 20
    # image_url ko readonly mat rakhna taaki tum link edit kar sako agar zaroorat pade
    readonly_fields = ('is_fb_posted', 'slug')

    fieldsets = (
        ('News Details', {
            # Yahan maine 'image_url' add kar diya hai
            'fields': ('title', 'content', 'category', 'district', 'url_city', 'image', 'image_url', 'youtube_url')
        }),
        ('Facebook Control', {
            'fields': ('share_now_to_fb', 'is_fb_posted'),
        }),
        ('SEO & Metadata', {
            'fields': ('meta_keywords', 'slug', 'is_important', 'date'),
            'classes': ('collapse',),
        }),
    )