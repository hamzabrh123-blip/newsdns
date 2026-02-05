from django.contrib import admin
from django.db import models 
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'category', 'date', 'is_important', 'share_now_to_fb', 'is_fb_posted')
    list_filter = ('district', 'category', 'date', 'is_important', 'is_fb_posted')
    search_fields = ('title', 'content')
    list_editable = ('is_important', 'share_now_to_fb')
    list_per_page = 20
    readonly_fields = ('is_fb_posted', 'slug', 'category', 'url_city')

    # Add/Edit page formatting
    formfield_overrides = {
        models.CharField: {
            'widget': admin.widgets.AdminTextInputWidget(
                attrs={
                    'style': 'width: 100%; padding: 15px; font-size: 1.4rem; border: 2px solid #b91d1d; border-radius: 8px;'
                }
            )
        },
    }

    fieldsets = (
        ('Headline Section (Full Width)', {
            'fields': ('title',),
        }),
        ('Khabar ka Content', {
            'fields': ('content',)
        }),
        ('Location Control (Auto-Pilot)', {
            'fields': (('district', 'category', 'url_city'),),
            'description': 'Sirf District select karein, Category aur URL City apne aap set ho jayenge.'
        }),
        ('Media Section', {
            'fields': (('image', 'image_url'), 'youtube_url'),
        }),
        ('Facebook & Importance', {
            'fields': (('is_important', 'share_now_to_fb', 'is_fb_posted'),),
        }),
        ('Advanced SEO Settings', {
            'fields': ('slug', 'date'), # <--- Yahan se meta_keywords hata diya hai
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.save()
