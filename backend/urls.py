"""URL configuration for the rxdjango-dashboard project.

Django routes (admin, media) are listed first; ``reflex_mount(...)`` is the
final entry and provides the SPA catch-all for every Reflex page registered
via ``@template`` / ``@page`` across the project apps (auto-discovered from
``INSTALLED_APPS``).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.views.static import serve
from reflex_django.urls import reflex_mount

urlpatterns = [
    path("admin", RedirectView.as_view(url="/admin/", permanent=False)),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif getattr(settings, "SERVE_MEDIA", False):
    media_url = settings.MEDIA_URL.lstrip("/")
    urlpatterns += [
        re_path(
            rf"^{media_url}(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

urlpatterns += [
    reflex_mount(
        app_name="dashboard",
        django_prefix=("/admin",),
        rx_config={
            "frontend_port": 3000,
            "backend_port": 8000,
        },
    ),
]
