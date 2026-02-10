from django.contrib import admin
from django import forms
from .models import News
from .constants import UP_DISTRICTS, OTHER_CATEGORIES
from django.utils.html import format_html
import gc

# 1. Custom Form: Do alag dropdown dikhane ke liye
class NewsAdminForm(forms.ModelForm):
    # UP Districts Dropdown
    up_city = forms.ChoiceField(
        choices=[('', '---------')] + [(x[0], x[1]) for x in UP_DISTRICTS],
        required=False,
        label="UP के जिले (Select for Local News)"
    )
    # Other Categories Dropdown
    big_cat = forms.ChoiceField(
        choices=[('', '---------')] + [(x[0], x[1]) for x in OTHER_CATEGORIES],
        required=False,
        label="बड़ी कैटेगरी (Select for National/Sports etc.)"
    )

    class Meta:
        model = News
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Edit karte waqt purana data dropdown mein apne aap dikhe
        if self.instance and self.instance.district:
            dist = self.instance.district
            if any(dist == x[0] for x in UP_DISTRICTS):
                self.fields['up_city'].initial = dist
            elif any(dist == x[0] for x in OTHER_CATEGORIES):
                self.fields['big_cat'].initial = dist

    def clean(self):
        cleaned_data = super().clean()
        up_city = cleaned_data.get('up_city')
        big_cat = cleaned_data.get('big_cat')

        # Validation: Dono select nahi karne hain
        if up_city and big_cat:
            raise forms.ValidationError("Bhai, dono dropdown mat chuno! Sirf ek select karo.")
        
        # Jo bhi select kiya hai use 'district' field mein daal do
        if up_city:
            cleaned_data['district'] = up_city
        elif big_cat:
            cleaned_data['district'] = big_cat
        
        return cleaned_data

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    
    # List View Settings
    list_display = ('display_thumb', 'title', 'district', 'category', 'status', 'date')
    list_filter = ('status', 'district', 'category')
    search_fields = ('title',)
    list_editable = ('status',)

    # Edit Error Fix: Inhe readonly rakho taaki save conflict na ho
    readonly_fields = ('category', 'url_city', 'image_url', 'is_fb_posted', 'display_large_img')

    fieldsets = (
        ('News Content', {'fields': ('title', 'status', 'content')}),
        ('Selection (Dono mein se ek chuno)', {
            'fields': (('up_city', 'big_cat'),),
            'description': 'Dono ke upar --------- hai. Sirf wahi dropdown select karein jisme news dalni hai.'
        }),
        ('Media Section', {'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url')}),
        ('Automation & Settings', {'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted'))}),
        ('SEO & Metadata', {'fields': ('slug', 'date', 'meta_keywords'), 'classes': ('collapse',)}),
    )

    def display_thumb(self, obj):
        img = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img: return format_html('<img src="{}" style="width:50px;height:50px;border-radius:5px;object-fit:cover;"/>', img)
        return "No Pic"

    def display_large_img(self, obj):
        img = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img: return format_html('<img src="{}" style="max-width:300px;border-radius:10px;"/>', img)
        return "No Preview"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        gc.collect()
