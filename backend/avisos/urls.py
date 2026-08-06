from django.urls import path

from .views import AvisosView

app_name = "avisos"

urlpatterns = [
    path("", AvisosView.as_view(), name="avisos"),
]
