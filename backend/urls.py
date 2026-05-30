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
import reflex as rx

from core.secrets import secret_manager
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

_rx_config: dict[str, object] = {
    "frontend_port": 3000,
    "backend_port": 8000,
}

# When ``REDIS_URL`` is set (production / multi-worker deploys), share Reflex
# per-tab state across workers through Redis instead of process memory. Falls
# back to the default in-memory state manager when unset (single-worker dev).
_redis_url = secret_manager.get_secret("REDIS_URL", default=None)
if _redis_url:
    _rx_config["redis_url"] = _redis_url


urlpatterns += [
    reflex_mount(
        app_name="dashboard",
        django_prefix=("/admin","/media",),
        rx_config=_rx_config,
        plugins=[rx.plugins.RadixThemesPlugin()],

    ),
]
