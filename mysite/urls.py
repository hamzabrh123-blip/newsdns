from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

# शॉपिंग वाले व्यू से सैटमैप फंक्शन इम्पोर्ट करें
from shopping.views import sitemap_shop_xml

# --- BRANDING ---
admin.site.site_header = "Uttar World Management Portal"
admin.site.site_title = "Admin Control Center"
admin.site.index_title = "News Engine Dashboard"

def google_verify(request):
    return HttpResponse(
        "google-site-verification: google21a82f00fad0f9b3.html",
        content_type="text/html"
    )

urlpatterns = [
    # 1. Google Verification
    path("google21a82f00fad0f9b3.html", google_verify),
    
    # 2. Shopping Sitemap (सिर्फ शॉपिंग वाला यहाँ जोड़ा गया है)
    # इसका नाम sitemap-shop.xml रखा है ताकि न्यूज़ वाले से न टकराए
    path('sitemap-shop.xml', sitemap_shop_xml, name='sitemap_shop'),
    
    # 3. Admin & Editor
    path('control-panel/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # 4. SHOPPING
    path('shopping/', include('shopping.urls')), 

    # 5. NEWS
    # न्यूज़ का सैटमैप इसके अंदर पहले से ही चल रहा है
    path('', include('mynews.urls')), 
]

# PC पर टेस्टिंग के दौरान Static और Media फाइल्स दिखाने के लिए
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)