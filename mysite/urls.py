from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

# Shopping views se sitemap
from shopping.views import sitemap_shop_xml

# --- BRANDING ---
admin.site.site_header = "Uttar World Management Portal"
admin.site.site_title = "Admin Control Center"
admin.site.index_title = "Store Management Dashboard"

def google_verify(request):
    return HttpResponse(
        "google-site-verification: google21a82f00fad0f9b3.html",
        content_type="text/html"
    )

urlpatterns = [
    # 1. Google Verification
    path("google21a82f00fad0f9b3.html", google_verify),

    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
    path('images/favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
    # 2. Shopping Sitemap
    path('sitemap.xml', sitemap_shop_xml, name='sitemap_shop'),    
    
    # 3. Admin & Editor
    path('control-panel/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # 4. SHOPPING (ROOT par)
    path('', include('shopping.urls')), 
]

# PC par testing ke liye (Sahi tarika)
if settings.DEBUG:
    # Static files ke liye STATICFILES_DIRS ka use karo, STATIC_ROOT ka nahi
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if hasattr(settings, 'STATICFILES_DIRS') else settings.STATIC_ROOT)
    
    # Media files ke liye yeh sahi hai
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)