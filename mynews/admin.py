from django.contrib import admin
from django import forms
from .models import News
from .constants import LOCATION_DATA
from django.utils.html import format_html
import gc

# Constants से डेटा निकालकर Dropdown के लिए तैयार करना
# हम English Name (item[0]) को Value और Hindi Name (item[1]) को Label बनाएंगे
CATEGORY_CHOICES = [(item[0], f"{item[1]} ({item[0]})") for item in LOCATION_DATA]

class NewsAdminForm(forms.ModelForm):
    # Category और District दोनों के लिए Dropdown बना दिया है
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, help_text="Constants.py से चुनो")
    district = forms.ChoiceField(choices=CATEGORY_CHOICES, help_text="जिला चुनो")
    
    class Meta:
        model = News
        fields = '__all__'

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    
    # List view में क्या-क्या दिखेगा
    list_display = ('display_thumb', 'title', 'district', 'category', 'status', 'date')
    list_filter = ('status', 'district', 'category', 'date')
    search_fields = ('title', 'content')
    list_editable = ('status', 'category', 'district') # लिस्ट से ही तुरंत बदलो
    
    readonly_fields = ('image_url', 'is_fb_posted', 'display_large_img')
    
    fieldsets = (
        ('News Content', {'fields': ('title', 'status', 'content'),}),
        ('Location & Category', {'fields': (('district', 'category', 'url_city'),),}),
        ('Media', {'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url'),}),
        ('Settings', {'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted')),}),
        ('SEO', {'fields': ('slug', 'date', 'meta_keywords'), 'classes': ('collapse',),}),
    )

    def display_thumb(self, obj):
        # Image Upload की है या URL दिया है, दोनों चेक करेगा
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
        # मेमोरी साफ रखने के लिए
        super().save_model(request, obj, form, change)
        gc.collect()
