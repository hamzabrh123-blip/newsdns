from django.contrib import admin
from django import forms
from .models import News, NewsImage, SidebarWidget
from .constants import UP_DISTRICTS, OTHER_CATEGORIES
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings
from PIL import Image
import requests
import base64
import gc
import io
import os
from django.db import transaction

# --- 1. Thumbnail Optimization ---
def get_optimized_url(url, width=100, height=100, crop="fill"):
    if not url: return ""
    # अगर इमेज लोकल है (http नहीं है), तो Cloudinary को बायपास करो
    if not url.startswith('http'):
        return url
    cloud_name = "dvoqsrkkq" 
    if "res.cloudinary.com" not in url:
        return f"https://res.cloudinary.com/{cloud_name}/image/fetch/f_auto,q_auto,w_{width},h_{height},c_{crop}/{url}"
    return url

# --- 2. News Admin Form ---
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
            if any(dist == x[0] for x in UP_DISTRICTS):
                self.fields['up_city'].initial = dist
            elif any(dist == x[0] for x in OTHER_CATEGORIES):
                self.fields['big_cat'].initial = dist

    def clean(self):
        cleaned_data = super().clean()
        up_city = cleaned_data.get('up_city')
        big_cat = cleaned_data.get('big_cat')
        if up_city: cleaned_data['district'] = up_city
        elif big_cat: cleaned_data['district'] = big_cat
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
            # लोकल और लाइव दोनों के लिए सुरक्षित रास्ता
            optimized = get_optimized_url(img_url, width=100, height=80)
            return format_html('<img src="{}" style="width:70px;height:50px;border-radius:4px;border:1px solid #ddd;"/>', optimized)
        return "No Pic"

# --- 4. Main News Admin ---
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    inlines = [NewsImageInline]
    list_display = ('display_thumb', 'get_title_styled', 'district', 'status', 'date')
    list_filter = ('status', 'district', 'category', 'date')
    search_fields = ('title', 'content')
    list_editable = ('status',)
    readonly_fields = ('image_url', 'is_fb_posted', 'display_large_img')

    fieldsets = (
        ('मुख्य जानकारी', {'fields': ('title', 'status', 'content')}),
        ('लोकेशन और कैटेगरी', {'fields': (('up_city', 'big_cat'), 'district')}),
        ('मीडिया', {'fields': (('image', 'display_large_img'), 'image_url', 'youtube_url')}),
        ('सोशल मीडिया', {'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted'))}),
        ('SEO', {'fields': ('slug', 'date', 'meta_keywords'), 'classes': ('collapse',)}),
    )

    def display_thumb(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            optimized = get_optimized_url(img_url, width=80, height=80)
            return format_html('<img src="{}" style="width:45px;height:45px;border-radius:5px;object-fit:cover;border:1px solid #ccc;"/>', optimized)
        return "No Pic"

    def get_title_styled(self, obj):
        if obj.title:
            return obj.title[:80]
        return "No Title"

    def display_large_img(self, obj):
        img_url = obj.image_url if obj.image_url else (obj.image.url if obj.image else None)
        if img_url:
            optimized = get_optimized_url(img_url, width=400, height=250, crop="limit")
            return format_html('<img src="{}" style="max-width:350px;border-radius:8px;"/>', optimized)
        return "No Preview"

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            obj.district = form.cleaned_data.get('district')
            super().save_model(request, obj, form, change)

            if obj.image and not obj.image_url:
                try:
                    logo_path = os.path.join(settings.BASE_DIR, 'mynews', 'static', 'watermark.png')
                    if not os.path.exists(logo_path):
                        logo_path = r"C:\Users\siraj\uttarworld_project\mynews\static\watermark.png"
                    
                    img_file = obj.image.open()
                    base_image = Image.open(img_file).convert("RGBA")
                    width, height = base_image.size

                    if os.path.exists(logo_path):
                        logo = Image.open(logo_path).convert("RGBA")
                        logo.thumbnail((int(width * 0.18), int(width * 0.18)), Image.Resampling.LANCZOS)
                        base_image.paste(logo, (width - logo.width - 20, height - logo.height - 20), logo)

                    buffer = io.BytesIO()
                    base_image.convert("RGB").save(buffer, format="JPEG", quality=95)
                    image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

                    api_key = "d0528bc96d36a90b0cfbac9227174e41"
                    response = requests.post("https://api.imgbb.com/1/upload", data={"key": api_key, "image": image_data})
                    result = response.json()
                    
                    if result.get("success"):
                        News.objects.filter(id=obj.id).update(image_url=result["data"]["url"], image=None)
                except Exception as e:
                    print(f"Locha: {str(e)}")
        
        gc.collect()

@admin.register(SidebarWidget)
class SidebarWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'widget_type', 'order', 'active')
    list_editable = ('order', 'active')