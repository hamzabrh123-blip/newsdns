from django.contrib import admin
from django import forms
from .models import News
from django.utils.html import format_html
import gc

# --- CATEGORY CHOICES (Dropdown ke liye) ---
CATEGORY_CHOICES = [
    ('National', 'National (देश)'),
    ('International', 'International (दुनिया)'),
    ('Sports', 'Sports (खेल)'),
    ('Market', 'Market (बाज़ार)'),
    ('Bollywood', 'Bollywood (मनोरंजन)'),
    ('Technology', 'Technology (तकनीक)'),
    ('Crime', 'Crime (जुर्म)'),
    ('Other', 'Other (अन्य)'),
]

# --- Admin Form to add Dropdowns ---
class NewsAdminForm(forms.ModelForm):
    category = forms.ChoiceField(choices=CATEGORY_CHOICES)
    
    class Meta:
        model = News
        fields = '__all__'

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm  # Yeh line dropdown enable karegi
    
    list_display = ('display_thumb', 'title', 'district', 'category', 'status', 'share_now_to_fb', 'date')
    list_filter = ('status', 'district', 'category', 'date', 'share_now_to_fb')
    search_fields = ('title', 'content')
    list_editable = ('status', 'share_now_to_fb', 'category') # Ab list se bhi edit hoga!
    
    readonly_fields = ('image_url', 'is_fb_posted', 'display_large_img')
    
    fieldsets = (
        ('News Content', {'fields': ('title', 'status', 'content'),}),
        ('Location & Category', {'fields': (('district', 'category', 'url_city'),),}),
        ('Media', {'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url'),}),
        ('Settings', {'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted')),}),
        ('SEO', {'fields': ('slug', 'date', 'meta_keywords'), 'classes': ('collapse',),}),
    )

    def display_thumb(self, obj):
        # Yahan humne upload ki hui image aur link dono ko check kiya hai
        img_src = obj.image.url if obj.image else obj.image_url
        if img_src:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', img_src)
        return "No Pic"

    def display_large_img(self, obj):
        img_src = obj.image.url if obj.image else obj.image_url
        if img_src:
            return format_html('<img src="{}" style="max-width: 300px; border-radius: 10px;" />', img_src)
        return "No Preview"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        gc.collect()
