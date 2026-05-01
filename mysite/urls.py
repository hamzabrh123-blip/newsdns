from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

# --- SITEMAP IMPORTS ---
from django.contrib.sitemaps.views import sitemap
from shopping.sitemaps import ProductSitemap  # शॉपिंग सैटमैप
# अपनी न्यूज़ वाली सैटमैप क्लास भी यहाँ इम्पोर्ट कर लेना अगर अलग है

# --- SITEMAP CONFIG ---
sitemaps = {
    'products': ProductSitemap,
    # 'news': NewsSitemap, # अगर न्यूज़ का सैटमैप बना रखा है तो यहाँ जोड़ दे
}

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
    
    # 2. Sitemap (नया जोड़ा गया)
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # 3. Admin & Editor
    path('control-panel/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # 4. SHOPPING
    path('shopping/', include('shopping.urls')), 

    # 5. NEWS
    path('', include('mynews.urls')), 
]

# PC पर टेस्टिंग के दौरान Static और Media फाइल्स दिखाने के लिए
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)