from django.contrib import admin
from django import forms
from .models import News, NewsImage, SidebarWidget
from .constants import UP_DISTRICTS, OTHER_CATEGORIES
from django.utils.html import format_html
import gc

# --- 1. Cloudinary Optimization (Admin Thumbnail ke liye) ---
def get_optimized_url(url, width=100, height=100, crop="fill"):
    if not url: return None
    cloud_name = "dvoqsrkkq" 
    if "res.cloudinary.com" not in url:
        return f"https://res.cloudinary.com/{cloud_name}/image/fetch/f_auto,q_auto,w_{width},h_{height},c_{crop}/{url}"
    return url

# --- 2. News Form Logic ---
class NewsAdminForm(forms.ModelForm):
    up_city = forms.ChoiceField(
        choices=[('', '---------')] + [(x[0], x[1]) for x in UP_DISTRICTS],
        required=False, label="UP के जिले"
    )
    big_cat = forms.ChoiceField(
        choices=[('', '---------')] + [(x[0], x[1]) for x in OTHER_CATEGORIES],
        required=False, label="बड़ी कैटेगरी (National/World)"
    )

    class Meta:
        model = News
        fields = '__all__'
        widgets = {'district': forms.HiddenInput()}

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
            raise forms.ValidationError("Bhai, dono dropdown mat chuno! Ek hi select karo.")
        if up_city: cleaned_data['district'] = up_city
        elif big_cat: cleaned_data['district'] = big_cat
        return cleaned_data

# --- 3. Multi-Image Inline (Ek news me kai photo ke liye) ---
class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1 # Kitne khali box dikhane hain
    readonly_fields = ('display_extra_thumb',)
    fields = ('image', 'display_extra_thumb', 'caption')

    def display_extra_thumb(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            optimized = get_optimized_url(img_url, width=100, height=80)
            return format_html('<img src="{}" style="width:60px;height:45px;border-radius:4px;"/>', optimized)
        return "No Pic"
    display_extra_thumb.short_description = "Preview"

# --- 4. Main News Admin ---
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    inlines = [NewsImageInline] # Multiple images yahan se add hongi
    
    list_display = ('display_thumb', 'title', 'district', 'category', 'status', 'date')
    list_filter = ('status', 'district', 'category', 'date')
    search_fields = ('title',)
    list_editable = ('status',)
    list_per_page = 20

    readonly_fields = ('category', 'url_city', 'image_url', 'is_fb_posted', 'display_large_img')

    fieldsets = (
        ('News Content', {'fields': ('title', 'status', 'content')}),
        ('Location/Category Selection', {'fields': (('up_city', 'big_cat'), 'district')}),
        ('Main Media Section', {'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url')}),
        ('Automation & Settings', {'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted'))}),
        ('SEO & Metadata', {'fields': ('slug', 'date', 'meta_keywords'), 'classes': ('collapse',)}),
    )

    def display_thumb(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            optimized = get_optimized_url(img_url, width=80, height=80)
            return format_html('<img src="{}" style="width:50px;height:50px;border-radius:5px;object-fit:cover;"/>', optimized)
        return "No Pic"
    display_thumb.short_description = "Thumb"

    def display_large_img(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            optimized = get_optimized_url(img_url, width=400, height=250, crop="limit")
            return format_html('<img src="{}" style="max-width:300px;border-radius:10px;box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/>', optimized)
        return "No Preview"

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
