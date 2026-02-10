from django.contrib import admin
from django import forms
from .models import News
from .constants import UP_DISTRICTS, OTHER_CATEGORIES
from django.utils.html import format_html

# Admin Form Setup
class NewsAdminForm(forms.ModelForm):
    # Do alag dropdown banaye
    up_city = forms.ChoiceField(
        choices=[('', '---------')] + [(x[0], x[1]) for x in UP_DISTRICTS],
        required=False, 
        label="UP के जिले (Select If UP News)"
    )
    big_cat = forms.ChoiceField(
        choices=[('', '---------')] + [(x[0], x[1]) for x in OTHER_CATEGORIES],
        required=False, 
        label="बड़ी कैटेगरी (Select If National/Sports etc.)"
    )

    class Meta:
        model = News
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        up_city = cleaned_data.get('up_city')
        big_cat = cleaned_data.get('big_cat')

        # Agar dono select kiye ya dono khali chhode
        if up_city and big_cat:
            raise forms.ValidationError("Bhai, dono dropdown mat chuno! Sirf ek select karo.")
        if not up_city and not big_cat:
            raise forms.ValidationError("Kam se kam ek cheez toh chuno (District ya Category)!")

        # Jo bhi select kiya use main 'district' field mein daal do
        cleaned_data['district'] = up_city if up_city else big_cat
        return cleaned_data

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ('display_thumb', 'title', 'district', 'category', 'status')
    list_editable = ('status',)
    readonly_fields = ('category', 'url_city', 'image_url', 'is_fb_posted', 'display_large_img')

    fieldsets = (
        ('News Content', {'fields': ('title', 'status', 'content')}),
        ('Selection (Dono mein se ek chuno)', {
            'fields': ('up_city', 'big_cat'),
            'description': 'UP ki news hai toh shehar chuno, warna badi category chuno.'
        }),
        ('Media', {'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url')}),
        ('Settings', {'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted'))}),
        ('SEO (Auto-Generated)', {'fields': ('slug', 'category', 'url_city'), 'classes': ('collapse',)}),
    )

    def display_thumb(self, obj):
        img = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img: return format_html('<img src="{}" style="width:50px;height:50px;border-radius:5px;"/>', img)
        return "No Pic"

    def display_large_img(self, obj):
        img = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img: return format_html('<img src="{}" style="max-width:300px;border-radius:10px;"/>', img)
        return "Preview"
