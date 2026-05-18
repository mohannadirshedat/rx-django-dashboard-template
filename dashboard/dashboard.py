"""Welcome to Reflex!."""

# Import all the pages.
import reflex as rx
from reflex_django.auth import add_auth_pages

from . import styles
from .pages import *

# Create the app.
app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
)
add_auth_pages(app)
