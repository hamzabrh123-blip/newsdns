from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

# Shopping views se sitemap aur google_verify
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

    # 2. Favicon direct serve without 302 redirect (Direct 200 OK)
    path('favicon.ico', serve, {'document_root': os.path.join(settings.BASE_DIR, 'shopping/static/images'), 'path': 'favicon.ico'}),
    path('images/favicon.ico', serve, {'document_root': os.path.join(settings.BASE_DIR, 'shopping/static/images'), 'path': 'favicon.ico'}),

    # 3. Admin & Editor
    path('control-panel/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('feedback/', include('feedback.urls')),

    path("api/fsj/", include("fsj_jewellery.urls")),
    
    # 4. SHOPPING (ROOT par)
    path('', include('shopping.urls')), 
]

# Static aur Media files handling
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if hasattr(settings, 'STATICFILES_DIRS') else settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production ke liye direct static serve fallback agar bina whitenoise ke serve karna pade
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
    ]