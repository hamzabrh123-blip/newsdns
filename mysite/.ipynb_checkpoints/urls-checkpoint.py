from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mynews.urls')),  # ✅ add this
]

"""urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
]
"""
