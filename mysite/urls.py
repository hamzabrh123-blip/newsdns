from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.template.loader import render_to_string
from mynews import views
from mynews.views import create_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mynews.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

urlpatterns += [
    path("create-admin/", create_admin),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-verify/", views.admin_verify, name="admin_verify"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
