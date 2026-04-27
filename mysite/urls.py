from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import User

# --- BRANDING: Django ka naam mitao ---
admin.site.site_header = "Uttar World Management Portal"
admin.site.site_title = "Admin Control Center"
admin.site.index_title = "News Engine Dashboard"

# --- Admin Creation Logic (Security ke liye sirf Debug mode mein rakho) ---
def create_admin(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "Halchal@2026")
        return HttpResponse("<h1>Success: Admin Created!</h1>")
    return HttpResponse("<h1>Error: Admin already exists!</h1>")

def google_verify(request):
    return HttpResponse(
        "google-site-verification: google21a82f00fad0f9b3.html",
        content_type="text/html"
    )

urlpatterns = [
    path('control-panel/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # 1. शॉपिंग को न्यूज़ से ऊपर रख ताकि न्यूज़ वाला 'slug' इसे न पकड़ ले
    path('shopping/', include('shopping.urls')), 

    # 2. बाकी सब न्यूज़ के हवाले
    path('news/', include('mynews.urls')), 
    path('', include('mynews.urls')), 
]

# 5. Temporary route (Sirf emergency ke liye, use ke baad hata dena)
if settings.DEBUG:
    urlpatterns += [path('make-me-admin-2026/', create_admin)]

# 6. Static aur Media files ka setup
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
