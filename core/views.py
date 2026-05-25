"""Reflex pages for the core app (settings + about). Auto-discovered by reflex-django."""

from pathlib import Path

import reflex as rx

from core.components.color_picker import primary_color_picker, secondary_color_picker
from core.components.radius_picker import radius_picker
from core.components.scaling_picker import scaling_picker
from dashboard import styles
from dashboard.templates import template


@template(route="/settings", title="Settings", login_required=True)
def settings() -> rx.Component:
    """Render the theme settings page."""
    return rx.vstack(
        rx.heading("Settings", size="5"),
        rx.vstack(
            rx.hstack(
                rx.icon("palette", color=rx.color("accent", 10)),
                rx.heading("Primary color", size="6"),
                align="center",
            ),
            primary_color_picker(),
            spacing="4",
            width="100%",
        ),
        rx.vstack(
            rx.hstack(
                rx.icon("blend", color=rx.color("gray", 11)),
                rx.heading("Secondary color", size="6"),
                align="center",
            ),
            secondary_color_picker(),
            spacing="4",
            width="100%",
        ),
        radius_picker(),
        scaling_picker(),
        spacing="7",
        width="100%",
    )


@template(route="/about", title="About", login_required=True)
def about() -> rx.Component:
    """Render the project README inside the dashboard shell."""
    with Path("README.md").open(encoding="utf-8") as readme:
        content = readme.read()
    return rx.markdown(content, component_map=styles.markdown_style)
