"""Reflex pages for the accounts app (auto-discovered by reflex-django)."""

import reflex as rx

from accounts.components.profile_avatar import profile_avatar_section
from accounts.components.profile_input import profile_input
from accounts.state import ProfileState
from dashboard.templates import template


@template(
    route="/profile",
    title="Profile",
    on_load=ProfileState.on_load_profile,
    login_required=True,
)
def profile() -> rx.Component:
    """Render the user's profile page inside the dashboard shell."""
    return rx.vstack(
        rx.vstack(
            rx.hstack(
                rx.icon("image"),
                rx.heading("Profile photo", size="5"),
                align="center",
            ),
            rx.text("Upload a photo for your account.", size="3"),
            profile_avatar_section(),
            width="100%",
            spacing="4",
        ),
        rx.divider(),
        rx.flex(
            rx.vstack(
                rx.hstack(
                    rx.icon("square-user-round"),
                    rx.heading("Personal information", size="5"),
                    align="center",
                ),
                rx.text("Update your personal information.", size="3"),
                width="100%",
            ),
            rx.form.root(
                rx.vstack(
                    profile_input(
                        "Name",
                        "name",
                        "Admin",
                        "text",
                        "user",
                        ProfileState.display_name,
                    ),
                    rx.button("Update", type="submit", width="100%"),
                    width="100%",
                    spacing="5",
                ),
                on_submit=ProfileState.handle_submit,
                reset_on_submit=True,
                width="100%",
                max_width="325px",
            ),
            width="100%",
            spacing="4",
            flex_direction=["column", "column", "row"],
        ),
        rx.divider(),
        rx.flex(
            rx.vstack(
                rx.hstack(
                    rx.icon("bell"),
                    rx.heading("Notifications", size="5"),
                    align="center",
                ),
                rx.text("Manage your notification settings.", size="3"),
            ),
            rx.checkbox(
                "Receive product updates",
                size="3",
                checked=ProfileState.notifications_enabled,
                on_change=ProfileState.toggle_notifications,
            ),
            width="100%",
            spacing="4",
            justify="between",
            flex_direction=["column", "column", "row"],
        ),
        spacing="6",
        width="100%",
        max_width="800px",
    )
