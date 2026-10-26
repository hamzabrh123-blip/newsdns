from django.urls import path
from .api import create_jewellery

urlpatterns = [
    path("jewellery/", create_jewellery, name="create_jewellery"),
]