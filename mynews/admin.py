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
    readonly_fields = ('is_fb_posted', 'slug')

    formfield_overrides = {
        models.CharField: {
            'widget': admin.widgets.AdminTextInputWidget(
                attrs={
                    'style': 'width: 100% !important; min-width: 900px; padding: 12px; font-size: 1.2rem; font-weight: bold; border: 2px solid #b91d1d; border-radius: 8px;'
                }
            )
        },
    }

    fieldsets = (
        ('Headline Section (Broad View)', {
            'fields': ('title',),
            'description': 'Headline ko yahan bada aur saaf-saaf likhein.'
        }),
        ('Khabar ka Content', {
            'fields': ('content',)
        }),
        ('Big Controller (Category & Location)', {
            'fields': (('category', 'district', 'url_city'),),
            'description': 'Select karein ki news kahan dikhani hai.'
        }),
        ('Media Section', {
            'fields': (('image', 'image_url'), 'youtube_url'),
        }),
        ('Facebook Automation', {
            'fields': (('share_now_to_fb', 'is_fb_posted'),),
        }),
        ('Advanced SEO & Settings', {
            'fields': ('meta_keywords', 'slug', 'is_important', 'date'),
            'classes': ('collapse',),
        }),
    )

    # FINAL FIX: super().save_model ko hataya hai taaki Cloudinary dubara file na maange
    def save_model(self, request, obj, form, change):
        obj.save()
