from django.contrib import admin
from django.db import models 
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    # List view mein columns ko set kiya
    list_display = ('title', 'district', 'category', 'date', 'is_important', 'share_now_to_fb', 'is_fb_posted')
    list_filter = ('district', 'category', 'date', 'is_important', 'is_fb_posted')
    search_fields = ('title', 'content')
    list_editable = ('is_important', 'share_now_to_fb')
    list_per_page = 20
    # Category aur URL City ab auto-fill hoti hain isliye readonly rakha hai
    readonly_fields = ('is_fb_posted', 'slug', 'category', 'url_city')

    # --- Yahan se hum Title ko Chauda aur Checkbox ko Patla karenge ---
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_admin_css'] = """
            <style>
                /* Title column ko failane ke liye */
                .field-title { min-width: 400px !important; font-weight: bold; color: #b91d1d; }
                
                /* Checkboxes wale columns ko ekdum slim karne ke liye */
                .column-is_important, .column-share_now_to_fb, .column-is_fb_posted { 
                    width: 80px !important; 
                    text-align: center; 
                }
                .action-checkbox-column { width: 30px !important; }
                
                /* Table ki readability badhane ke liye */
                #result_list thead th { background: #f8f8f8; color: #333; }
            </style>
        """
        return super().changelist_view(request, extra_context=extra_context)

    # Add/Edit page par Title box ko bada dikhane ke liye
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
            'fields': ('meta_keywords', 'slug', 'date'),
            'classes': ('collapse',),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Seedha model ka save method call hoga (Magic logic wahan hai)
        obj.save()
