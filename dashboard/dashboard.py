"""Welcome to Reflex!."""

# Import all the pages.
import reflex as rx
from reflex_django.conf import configure_django
from reflex_django.auth import (
    register_login_page,
    register_register_page,
    register_password_reset_page,
    register_password_reset_confirm_page,
    get_auth_settings,
)

from . import styles
from .pages import *
from .pages.auth import (
    CustomLoginPage,
    CustomRegisterPage,
    CustomPasswordResetPage,
    CustomPasswordResetConfirmPage,
)

# Create the app.
app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
)

# Initialize Django environment and register custom inherited authentication pages
configure_django()
auth = get_auth_settings()
if auth.enabled:
    register_login_page(app, page=CustomLoginPage, settings=auth)
    if auth.signup_enabled:
        register_register_page(app, page=CustomRegisterPage, settings=auth)
    if auth.password_reset_enabled:
        register_password_reset_page(app, page=CustomPasswordResetPage, settings=auth)
        register_password_reset_confirm_page(app, page=CustomPasswordResetConfirmPage, settings=auth)

