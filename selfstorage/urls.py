from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.shortener.views import short_redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.storage_units.urls')),
    path("s/<str:token>/", short_redirect, name="short_redirect"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
