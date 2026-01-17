from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def google_verify(request):
    return HttpResponse(
        "google-site-verification: google21a82f00fad0f9b3.html",
        content_type="text/html"
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Google Verification
    path("google21a82f00fad0f9b3.html", google_verify),

    # CKEditor Uploader (यही आपकी फोटो अपलोड कराता है)
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # Main Website URLs (इसे नीचे ही रखें ताकि बाकी paths पहले चेक हों)
    path('', include('mynews.urls')),  
]

# Media और Static files के लिए (Production और Local दोनों में बेहतर काम करेगा)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
