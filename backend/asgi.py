"""ASGI entry point for the rxdjango-dashboard project.

The single application here is served by both ``manage.py run_reflex`` (dev)
and production ASGI servers (uvicorn, granian, hypercorn). It bridges Django
and Reflex through :mod:`reflex_django.asgi_entry`.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

from reflex_django.asgi_entry import application  # noqa: E402,F401
