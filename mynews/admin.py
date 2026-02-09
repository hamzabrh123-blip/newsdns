from django.contrib import admin
from django.db import models 
from .models import News
import gc

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    # 1. लिस्ट व्यू (Bahar ki list)
    list_display = ('title', 'district', 'status', 'is_important', 'show_in_highlights', 'share_now_to_fb', 'date')
    
    # 2. फिल्टर्स
    list_filter = ('status', 'district', 'category', 'date', 'is_important', 'show_in_highlights', 'share_now_to_fb')
    
    # 3. सर्च बार
    search_fields = ('title', 'content')
    
    # 4. बाहर से एडिट करने वाली फील्ड्स
    list_editable = ('is_important', 'show_in_highlights', 'status', 'share_now_to_fb')
    
    list_per_page = 20
    
    # Category aur URL City auto-fill hote hain, aur image_url ImgBB se aata hai
    # is_fb_posted ko bhi readonly rakha hai kyunki wo system handle karega
    readonly_fields = ('category', 'url_city', 'image_url', 'is_fb_posted')

    # Title बॉक्स को सुंदर बनाने के लिए
    formfield_overrides = {
        models.CharField: {
            'widget': admin.widgets.AdminTextInputWidget(
                attrs={
                    'style': 'width: 100%; padding: 10px; font-size: 1.2rem; border: 2px solid #b91d1d; border-radius: 5px;'
                }
            )
        },
    }

    # एडमिन लेआउट
    fieldsets = (
        ('मुख्य जानकारी (Title & Content)', {
            'fields': ('title', 'status', 'content'),
        }),
        ('स्थान और कैटेगरी (Location Control)', {
            'fields': (('district', 'category', 'url_city'),),
        }),
        ('मीडिया (Image & Video)', {
            'fields': (('image', 'image_url'), 'youtube_url'),
            'description': 'Image अपलोड करें, ImgBB लिंक अपने आप जनरेट होकर image_url में आ जाएगा।',
        }),
        ('सोशल मीडिया और हाइलाइट्स', {
            'fields': (('is_important', 'show_in_highlights'), ('share_now_to_fb', 'is_fb_posted')),
            'description': 'यहीं से आप न्यूज़ को Facebook पर शेयर करने का कंट्रोल कर सकते हैं।',
        }),
        ('एडवांस्ड सेटिंग्स (SEO)', {
            'fields': ('slug', 'date', 'meta_keywords'), 
            'classes': ('collapse',), # SEO सेटिंग्स को छुपा कर रखा है
        }),
    )

    def save_model(self, request, obj, form, change):
        # मॉडल का अपना save() मेथड कॉल होगा जहाँ वॉटरमार्क और ImgBB लॉजिक है
        super().save_model(request, obj, form, change)
        # RAM साफ़ करना
        gc.collect()

# Admin Header Customization
admin.site.site_header = "Uttar World Administration"
admin.site.site_title = "News Portal Admin"
admin.site.index_title = "Welcome to Uttar World News Dashboard"
