"""Public website URL configuration (maridav.ci)."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


urlpatterns = [
    path("api/v1/", include("crm.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("", include("website.urls")),
]
