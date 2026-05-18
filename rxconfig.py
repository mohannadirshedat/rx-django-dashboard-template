import reflex as rx
from reflex_django import ReflexDjangoPlugin
config = rx.Config(
    app_name="dashboard",
    plugins=[
        ReflexDjangoPlugin(
            settings_module="backend.settings",
            admin_prefix="/admin",
            backend_prefix="/api",
            extra_prefixes=("/media",),
        ),
        rx.plugins.SitemapPlugin(),
        rx.plugins.RadixThemesPlugin(),

    ],
    show_built_with_reflex=False
)
