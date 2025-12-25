from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mynews import views
from mynews.views import create_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mynews.urls')),  # Main app urls
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # Custom admin paths
    path('create-admin/', create_admin),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-verify/', views.admin_verify, name='admin_verify'),
]

# Serve media files during DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
