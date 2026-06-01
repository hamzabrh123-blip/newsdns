from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView # <--- Redirect ke liye import

# Shopping views se sitemap
from shopping.views import sitemap_shop_xml

# --- BRANDING ---
admin.site.site_header = "Uttar World Management Portal"
admin.site.site_title = "Admin Control Center"
admin.site.index_title = "Store Management Dashboard" # News Engine hata diya

def google_verify(request):
    return HttpResponse(
        "google-site-verification: google21a82f00fad0f9b3.html",
        content_type="text/html"
    )

urlpatterns = [
    # 1. Google Verification
    path("google21a82f00fad0f9b3.html", google_verify),
    
    # 2. Shopping Sitemap (Ab ye root sitemap ban jayega)
    path('sitemap.xml', sitemap_shop_xml, name='sitemap_shop'),    
    
    # 3. Admin & Editor
    path('control-panel/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # 4. SHOPPING (Ab ye ROOT par chalega)
    path('', include('shopping.urls')), 
]

# PC par testing ke liye
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 5. CATCH-ALL REDIRECT (News hatane ke baad SEO bachane ke liye)
# Agar koi purani news link par click karega, toh wo seedha home page par aayega
urlpatterns += [
    path('news/', RedirectView.as_view(url='/', permanent=True)),
    path('mynews/', RedirectView.as_view(url='/', permanent=True)),
]