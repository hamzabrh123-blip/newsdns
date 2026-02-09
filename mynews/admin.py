from django.contrib import admin
from django.db import models
from .models import News
from django.utils.html import format_html
import gc


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):

    list_display = (
        'title', 'district', 'status',
        'is_important', 'show_in_highlights',
        'share_now_to_fb', 'date'
    )

    list_filter = (
        'status', 'district', 'category',
        'date', 'is_important',
        'show_in_highlights', 'share_now_to_fb'
    )

    search_fields = ('title', 'content')

    list_editable = (
        'is_important',
        'show_in_highlights',
        'status',
        'share_now_to_fb'
    )

    list_per_page = 20

    readonly_fields = (
        'category',
        'url_city',
        'image_url',
        'is_fb_posted'
    )

    formfield_overrides = {
        models.CharField: {
            'widget': admin.widgets.AdminTextInputWidget(
                attrs={
                    'style': (
                        'width:100%; padding:10px; '
                        'font-size:1.2rem; '
                        'border:2px solid #b91d1d; '
                        'border-radius:5px;'
                    )
                }
            )
        },
    }

    fieldsets = (
        ('मुख्य जानकारी (Title & Content)', {
            'fields': ('title', 'status', 'content'),
        }),
        ('स्थान और कैटेगरी (Location Control)', {
            'fields': (('district', 'category', 'url_city'),),
        }),
        ('मीडिया (Image & Video)', {
            'fields': (('image', 'image_url'), 'youtube_url'),
            'description': 'Image upload karein, ImgBB link auto-generate hoga.',
        }),
        ('सोशल मीडिया और हाइलाइट्स', {
            'fields': (
                ('is_important', 'show_in_highlights'),
                ('share_now_to_fb', 'is_fb_posted')
            ),
            'description': 'Facebook sharing control yahin se hoga.',
        }),
        ('एडवांस्ड सेटिंग्स (SEO)', {
            'fields': ('slug', 'date', 'meta_keywords'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        gc.collect()


# Admin Branding
admin.site.site_header = "Uttar World Administration"
admin.site.site_title = "News Portal Admin"
admin.site.index_title = "Welcome to Uttar World News Dashboard"
