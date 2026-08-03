from django.urls import path

from core.saude import health_check

urlpatterns = [
    path("health/", health_check, name="health-check"),
]
