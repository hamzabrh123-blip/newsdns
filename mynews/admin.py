from django.contrib import admin
from django import forms
from .models import News
from .constants import UP_DISTRICTS, OTHER_CATEGORIES
from django.utils.html import format_html
import gc

# Cloudinary Optimization का छोटा सा फंक्शन यहाँ बना लेते हैं ताकि बार-बार न लिखना पड़े
def get_optimized_url(url, width=100, height=100, crop="fill"):
    if not url: return None
    # अगर URL पहले से क्लाउडिनरी का नहीं है, तो अपना गेटवे लगा दो
    cloud_name = "dbe9v8mca"  # आपका क्लाउड नाम
    return f"https://res.cloudinary.com/{cloud_name}/image/fetch/f_auto,q_auto,w_{width},h_{height},c_{crop}/{url}"

class NewsAdminForm(forms.ModelForm):
    # ... (आपका पुराना Dropdown लॉजिक एकदम सही है, इसे छेड़ने की ज़रूरत नहीं) ...
    up_city = forms.ChoiceField(
        choices=[('', '---------')] + [(x[0], x[1]) for x in UP_DISTRICTS],
        required=False,
        label="UP के जिले (Select for Local News)"
    )
    big_cat = forms.ChoiceField(
        choices=[('', '---------')] + [(x[0], x[1]) for x in OTHER_CATEGORIES],
        required=False,
        label="बड़ी कैटेगरी (Select for National/Sports etc.)"
    )

    class Meta:
        model = News
        fields = '__all__'
        widgets = {
            'district': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        if up_city and big_cat:
            raise forms.ValidationError("Bhai, dono dropdown mat chuno! Sirf ek select karo.")
        if up_city:
            cleaned_data['district'] = up_city
        elif big_cat:
            cleaned_data['district'] = big_cat
        return cleaned_data

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    
    list_display = ('display_thumb', 'title', 'district', 'category', 'status', 'date')
    list_filter = ('status', 'district', 'category')
    search_fields = ('title',)
    list_editable = ('status',)

    readonly_fields = ('category', 'url_city', 'image_url', 'is_fb_posted', 'display_large_img')

    # ... (Fieldsets logic stays the same) ...
    fieldsets = (
        ('News Content', {'fields': ('title', 'status', 'content')}),
        ('Selection', {'fields': (('up_city', 'big_cat'), 'district')}),
        ('Media Section', {'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url')}),
        ('Automation & Settings', {'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted'))}),
        ('SEO & Metadata', {'fields': ('slug', 'date', 'meta_keywords'), 'classes': ('collapse',)}),
    )

    def display_thumb(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            # एडमिन लिस्ट के लिए इमेज को 80x80 पर क्रॉप कर दिया ताकि लिस्ट तुरंत लोड हो
            optimized = get_optimized_url(img_url, width=80, height=80)
            return format_html('<img src="{}" style="width:50px;height:50px;border-radius:5px;object-fit:cover;border:1px solid #ddd;"/>', optimized)
        return "No Pic"

    def display_large_img(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            # प्रीव्यू के लिए थोड़ा बड़ा साइज (400px width)
            optimized = get_optimized_url(img_url, width=400, height=250, crop="limit")
            return format_html('<img src="{}" style="max-width:300px;border-radius:10px;box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/>', optimized)
        return "No Preview"

    def save_model(self, request, obj, form, change):
        obj.district = form.cleaned_data.get('district')
        super().save_model(request, obj, form, change)
        gc.collect()
