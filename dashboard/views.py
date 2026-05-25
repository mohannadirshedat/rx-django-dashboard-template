"""Reflex pages for the dashboard shell app (auto-discovered by reflex-django).

The dashboard app itself does not own any business pages — those live in
``accounts/views.py``, ``analytics/views.py``, ``items/views.py``, and
``core/views.py``. What ``dashboard/views.py`` does is register the dashboard's
custom-branded auth pages (login, register, password reset) by hooking into
:func:`reflex_django.page`.

The decorator is applied to the page **class** (a :class:`reflex_django.auth.BaseAuthPage`
subclass); Reflex calls it with ``()`` at render time and the
``AuthPageMeta`` metaclass returns the page component.
"""

from reflex_django import page
from reflex_django.auth import get_auth_settings

from dashboard.auth import (
    CustomLoginPage,
    CustomPasswordResetConfirmPage,
    CustomPasswordResetPage,
    CustomRegisterPage,
)


def _register_auth_page(page_cls, *, route: str) -> None:
    kwargs: dict = {"route": route, "title": page_cls.default_title}
    on_load = page_cls.default_on_load
    if on_load is not None:
        kwargs["on_load"] = on_load
    page(**kwargs)(page_cls)


_auth = get_auth_settings()

if _auth.enabled:
    _register_auth_page(CustomLoginPage, route=_auth.login_url)

    if _auth.signup_enabled:
        _register_auth_page(CustomRegisterPage, route=_auth.signup_url)

    if _auth.password_reset_enabled:
        _register_auth_page(CustomPasswordResetPage, route=_auth.password_reset_url)
        _register_auth_page(
            CustomPasswordResetConfirmPage,
            route=_auth.password_reset_confirm_url,
        )
