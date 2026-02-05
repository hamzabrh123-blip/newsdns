from django.contrib import admin
from django.db import models 
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    # Admin List view mein kya-kya dikhega
    list_display = ('title', 'district', 'category', 'date', 'is_important', 'share_now_to_fb', 'is_fb_posted')
    list_filter = ('district', 'category', 'date', 'is_important', 'is_fb_posted')
    search_fields = ('title', 'content')
    list_editable = ('is_important', 'share_now_to_fb')
    list_per_page = 20
    
    # SLUG KO READONLY SE HATA DIYA HAI taaki tu edit kar sake
    # Category aur url_city auto-pilot hain toh unhe readonly rehne de
    readonly_fields = ('is_fb_posted', 'category', 'url_city')

    # Heading dabba (Title) ko bada aur laal border dene ke liye formatting
    formfield_overrides = {
        models.CharField: {
            'widget': admin.widgets.AdminTextInputWidget(
                attrs={
                    'style': 'width: 100%; padding: 15px; font-size: 1.4rem; border: 2px solid #b91d1d; border-radius: 8px;'
                }
            )
        },
    }

    # Admin panel ke sections (Fields)
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
            'fields': ('slug', 'date'), 
            'description': 'Slug khali chhod dein auto-generate karne ke liye. Edit karna ho toh yahan se badlein.',
            'classes': ('collapse',), # Isse ye section default mein band rahega
        }),
    )

    def save_model(self, request, obj, form, change):
        # Jab tu "Save" dabayega, toh ye model.py ke save() ko trigger karega
        # Jahan humne slug banane ka logic likha hai
        obj.save()
