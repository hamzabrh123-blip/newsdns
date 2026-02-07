from django.contrib import admin
from django.db import models 
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'category', 'date', 'is_important') # FB fields hata diye
    list_filter = ('district', 'category', 'date', 'is_important')
    search_fields = ('title', 'content')
    list_editable = ('is_important',) 
    list_per_page = 20
    
    readonly_fields = ('category', 'url_city')

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
        }),
        ('Media Section', {
            'fields': (('image', 'image_url'), 'youtube_url'),
        }),
        ('Importance', {
            'fields': ('is_important',), # FB fields yahan se bhi hata diye
        }),
        ('Advanced SEO Settings', {
            'fields': ('slug', 'date'), 
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.save()
