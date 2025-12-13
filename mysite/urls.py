from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.template.loader import render_to_string

from mynews import views
from mynews.views import create_admin


# ✅ ads.txt view
def ads_txt(request):
    content = render_to_string("ads.txt")
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ ads.txt ROOT par
    path('ads.txt', ads_txt),

    path('', include('mynews.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# Extra admin URLs
urlpatterns += [
    path("create-admin/", create_admin),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-verify/", views.admin_verify, name="admin_verify"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
