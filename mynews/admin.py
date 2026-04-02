from django.contrib import admin
from django import forms
from .models import News, NewsImage, SidebarWidget
from .constants import UP_DISTRICTS, OTHER_CATEGORIES
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import gc

# --- 1. Thumbnail Optimization ---
def get_optimized_url(url, width=100, height=100, crop="fill"):
    if not url: return ""
    cloud_name = "dvoqsrkkq" 
    # अगर URL पहले से क्लाउडिनरी का नहीं है, तो फेच प्रॉक्सी लगाओ
    if "res.cloudinary.com" not in url:
        return f"https://res.cloudinary.com/{cloud_name}/image/fetch/f_auto,q_auto,w_{width},h_{height},c_{crop}/{url}"
    return url

# --- 2. News Admin Form Logic ---
class NewsAdminForm(forms.ModelForm):
    up_city = forms.ChoiceField(
        choices=[('', '--- उत्तर प्रदेश के जिले ---')] + [(x[0], x[1]) for x in UP_DISTRICTS],
        required=False, label="UP के जिले"
    )
    big_cat = forms.ChoiceField(
        choices=[('', '--- अन्य बड़ी कैटेगरी ---')] + [(x[0], x[1]) for x in OTHER_CATEGORIES],
        required=False, label="National/World Category"
    )

    class Meta:
        model = News
        fields = '__all__'
        widgets = {'district': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.district:
            dist = self.instance.district
            if any(dist.lower() == x[0].lower() for x in UP_DISTRICTS):
                self.fields['up_city'].initial = dist
            elif any(dist.lower() == x[0].lower() for x in OTHER_CATEGORIES):
                self.fields['big_cat'].initial = dist

    def clean(self):
        cleaned_data = super().clean()
        up_city = cleaned_data.get('up_city')
        big_cat = cleaned_data.get('big_cat')
        
        if up_city and big_cat:
            raise forms.ValidationError("Bhai, UP District और Category दोनों मत चुनो! सिर्फ एक सिलेक्ट करो।")
        
        if up_city: 
            cleaned_data['district'] = up_city
        elif big_cat: 
            cleaned_data['district'] = big_cat
        elif not cleaned_data.get('district'):
            raise forms.ValidationError("कृपया जिला या कैटेगरी जरूर चुनें।")
            
        return cleaned_data

# --- 3. News Image Inline ---
class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    readonly_fields = ('display_extra_thumb',)
    fields = ('image', 'display_extra_thumb', 'caption')

    def display_extra_thumb(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            optimized = get_optimized_url(img_url, width=100, height=80)
            return format_html('<img src="{}" style="width:70px;height:50px;border-radius:4px;border:1px solid #ddd;"/>', optimized)
        return mark_safe("<span>No Pic</span>")
    display_extra_thumb.short_description = "Preview"

# --- 4. Main News Admin ---
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    inlines = [NewsImageInline]
    
    list_display = ('display_thumb', 'get_title_styled', 'district', 'category', 'status', 'get_status_badge', 'date')
    list_filter = ('status', 'district', 'category', 'date')
    search_fields = ('title', 'content')
    
    list_editable = ('status',)
    list_per_page = 20
    readonly_fields = ('category', 'url_city', 'image_url', 'is_fb_posted', 'display_large_img')

    fieldsets = (
        ('मुख्य जानकारी (News Content)', {
            'fields': ('title', 'status', 'content'),
        }),
        ('लोकेशन और कैटेगरी (Dynamic Select)', {
            'fields': (('up_city', 'big_cat'), 'district'),
        }),
        ('मीडिया (Main Image & Video)', {
            'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url'),
        }),
        ('सोशल मीडिया और हाईलाइट्स', {
            'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted')),
        }),
        ('SEO और तारीख', {
            'fields': ('slug', 'date', 'meta_keywords'),
            'classes': ('collapse',),
        }),
    )

    def get_title_styled(self, obj):
        important_tag = '<span style="color:red;font-weight:bold;">[Breaking]</span> ' if obj.is_important else ''
        highlight_tag = '<span style="color:orange;font-weight:bold;">[★]</span> ' if obj.show_in_highlights else ''
        # Django 6.0 compatibility fix
        return format_html('{}{}{}', mark_safe(important_tag), mark_safe(highlight_tag), obj.title[:80])
    get_title_styled.short_description = "Title"

    def get_status_badge(self, obj):
        colors = {'Published': '#28a745', 'Draft': '#ffc107'}
        return format_html('<span style="background:{}; color:white; padding:3px 8px; border-radius:10px; font-size:11px;">{}</span>', 
                            colors.get(obj.status, '#6c757d'), obj.status)
    get_status_badge.short_description = "Badge"

    def display_thumb(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            optimized = get_optimized_url(img_url, width=80, height=80)
            return format_html('<img src="{}" style="width:45px;height:45px;border-radius:5px;object-fit:cover;border:1px solid #ccc;"/>', optimized)
        # Fix for TypeError: args or kwargs must be provided
        return format_html('<div style="width:45px;height:45px;background:#eee;border-radius:5px;text-align:center;line-height:45px;color:#999;font-size:10px;">No Pic</div>', "")
    display_thumb.short_description = "Img"

    def display_large_img(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            optimized = get_optimized_url(img_url, width=400, height=250, crop="limit")
            return format_html('<div><img src="{}" style="max-width:350px;border-radius:8px;box-shadow: 0 4px 12px rgba(0,0,0,0.15); border:1px solid #ddd;"/><p style="color:gray;font-size:11px;">URL: {}</p></div>', optimized, obj.image_url or "Local Storage")
        return "Preview will appear after upload"

    def save_model(self, request, obj, form, change):
        obj.district = form.cleaned_data.get('district')
        super().save_model(request, obj, form, change)
        gc.collect()

# --- 5. Sidebar Widget Admin ---
@admin.register(SidebarWidget)
class SidebarWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'widget_type', 'order', 'active')
    list_editable = ('order', 'active')
    list_filter = ('widget_type', 'active')