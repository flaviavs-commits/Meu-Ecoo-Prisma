from django.urls import path

from .views import ArquivoDownloadView, ArquivoUploadView

app_name = "arquivos"

urlpatterns = [
    path("", ArquivoUploadView.as_view(), name="upload"),
    path("<int:pk>/download/", ArquivoDownloadView.as_view(), name="download"),
]
