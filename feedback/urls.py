
from django.urls import path
from . import views

app_name = "feedback"

urlpatterns = [
    path(
        "<str:target_type>/<slug:slug>/submit/",
        views.submit_feedback,
        name="submit_feedback",
    ),
]
