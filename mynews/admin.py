from django.contrib import admin
from django.db import models 
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    # 1. Bahar ki list mein kya-kya dikhega
    list_display = ('title', 'district', 'status', 'is_important', 'show_in_highlights', 'share_now_to_fb', 'is_fb_posted', 'date')
    
    # 2. Side mein filter karne ke liye
    list_filter = ('status', 'district', 'category', 'date', 'is_important', 'show_in_highlights')
    
    # 3. Search bar ke liye
    search_fields = ('title', 'content')
    
    # 4. Bina edit page khole bahar se hi tick karne ke liye
    list_editable = ('is_important', 'show_in_highlights', 'share_now_to_fb', 'status')
    
    list_per_page = 20
    readonly_fields = ('category', 'url_city', 'is_fb_posted')

    # Title ko bada aur stylish dikhane ke liye
    formfield_overrides = {
        models.CharField: {
            'widget': admin.widgets.AdminTextInputWidget(
                attrs={
                    'style': 'width: 100%; padding: 10px; font-size: 1.2rem; border: 2px solid #b91d1d; border-radius: 5px;'
                }
            )
        },
    }

    # Admin panel ka structure (Layout)
    fieldsets = (
        ('मुख्य जानकारी (Title & Content)', {
            'fields': ('title', 'status', 'content'),
        }),
        ('स्थान और कैटेगरी (Location Control)', {
            'fields': (('district', 'category', 'url_city'),),
        }),
        ('मीडिया (Image & Video)', {
            'fields': (('image', 'image_url'), 'youtube_url'),
        }),
        ('स्पेशल फीचर्स (Highlights & Sharing)', {
            'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted')),
            'description': 'यहीं से आप फेसबुक पर शेयर और टॉप 5 हाइलाइट्स सेट कर सकते हैं।',
        }),
        ('एडवांस्ड सेटिंग्स (SEO)', {
            'fields': ('slug', 'date', 'meta_keywords'), 
            'classes': ('collapse',), # Isko chhupa diya hai, click karne par khulega
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.save()
