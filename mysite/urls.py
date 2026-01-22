from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import User # Ye zaroori hai admin banane ke liye

# --- Naya Admin Banane Ka Jugaad (Bina Shell Ke) ---
def create_admin(request):
    # Aapka naya password yahan hai: Halchal@2026
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "Halchal@2026")
        return HttpResponse("<h1>Bhai, Admin Ban Gaya Hai!</h1><p>Ab /admin par login karo.</p>")
    return HttpResponse("<h1>Admin Pehle Se Hai!</h1>")
# -----------------------------------------------

def google_verify(request):
    return HttpResponse(
        "google-site-verification: google21a82f00fad0f9b3.html",
        content_type="text/html"
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Ye hai woh temporary rasta admin banane ke liye
    path('make-me-admin-2026/', create_admin),
    
    # Google Verification
    path("google21a82f00fad0f9b3.html", google_verify),

    # CKEditor Uploader 
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('', include('mynews.urls')),  
]

# Static aur Media files ka setup
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production (Render) ke liye static setup
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
