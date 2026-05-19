"""Custom authentication screens inheriting from reflex-django."""

import reflex as rx
from reflex_django.auth import LoginPage, RegisterPage, PasswordResetPage, PasswordResetConfirmPage
from ..templates.template import ThemeState

AUTH_CARD_MAX_WIDTH = "28em"
PADDING_TOP = "4rem"


def custom_brand_icon(*, size: int = 28) -> rx.Component:
    height = f"{size / 10}em" if size else "3em"
    return rx.image(src="/rxdjango-logo.png", height=height, border_radius="var(--radius-1)", margin_bottom="0.5em")


def custom_auth_card(*children: rx.Component, **props: object) -> rx.Component:
    """Centered card wrapper for auth forms matching the dashboard design system."""
    return rx.card(
        rx.vstack(*children, spacing="6", width="100%"),
        size="4",
        max_width=AUTH_CARD_MAX_WIDTH,
        width="100%",
        box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.08), 0 1px 2px 0 rgba(0, 0, 0, 0.04)",
        border_radius="var(--radius-3)",
        border=f"1px solid {rx.color('gray', 4)}",
        background_color=rx.color_mode_cond("white", rx.color("gray", 2)),
        class_name="auth-card",
        **props,
    )


def custom_auth_page_shell(content: rx.Component) -> rx.Component:
    """Vertically centered page layout for auth screens with a theme toggle and proper theme wrapper."""
    return rx.theme(
        rx.box(
            rx.box(
                rx.color_mode.button(style={"opacity": "0.8", "scale": "0.95"}),
                position="absolute",
                top="1.5rem",
                right="1.5rem",
                z_index="10",
            ),
            rx.center(
                content,
                padding_top=PADDING_TOP,
                padding_x="1rem",
                min_height="100vh",
                width="100%",
            ),
            width="100%",
            min_height="100vh",
            position="relative",
            background=rx.color_mode_cond(
                f"linear-gradient(135deg, {rx.color('gray', 1)} 0%, {rx.color('gray', 3)} 100%)",
                f"linear-gradient(135deg, {rx.color('gray', 1)} 0%, {rx.color('gray', 2)} 100%)"
            ),
        ),
        has_background=True,
        accent_color=ThemeState.accent_color,
        gray_color=ThemeState.gray_color,
        radius=ThemeState.radius,
        scaling=ThemeState.scaling,
    )


class CustomLoginPage(LoginPage):
    @classmethod
    def shell(cls, content: rx.Component) -> rx.Component:
        return custom_auth_page_shell(content)

    @classmethod
    def card(cls, *children: rx.Component, **props: object) -> rx.Component:
        return custom_auth_card(*children, **props)

    @classmethod
    def heading(cls) -> rx.Component:
        return rx.center(
            custom_brand_icon(),
            rx.heading(
                cls.heading_text(),
                size="6",
                as_="h2",
                text_align="center",
                width="100%",
            ),
            direction="column",
            spacing="5",
            width="100%",
        )


class CustomRegisterPage(RegisterPage):
    @classmethod
    def shell(cls, content: rx.Component) -> rx.Component:
        return custom_auth_page_shell(content)

    @classmethod
    def card(cls, *children: rx.Component, **props: object) -> rx.Component:
        return custom_auth_card(*children, **props)

    @classmethod
    def heading(cls) -> rx.Component:
        return rx.center(
            custom_brand_icon(),
            rx.heading(
                cls.heading_text(),
                size="6",
                as_="h2",
                text_align="center",
                width="100%",
            ),
            direction="column",
            spacing="5",
            width="100%",
        )


class CustomPasswordResetPage(PasswordResetPage):
    @classmethod
    def shell(cls, content: rx.Component) -> rx.Component:
        return custom_auth_page_shell(content)

    @classmethod
    def card(cls, *children: rx.Component, **props: object) -> rx.Component:
        return custom_auth_card(*children, **props)

    @classmethod
    def heading(cls) -> rx.Component:
        return rx.center(
            custom_brand_icon(),
            rx.heading(
                cls.heading_text(),
                size="6",
                as_="h2",
                text_align="center",
                width="100%",
            ),
            direction="column",
            spacing="5",
            width="100%",
        )


class CustomPasswordResetConfirmPage(PasswordResetConfirmPage):
    @classmethod
    def shell(cls, content: rx.Component) -> rx.Component:
        return custom_auth_page_shell(content)

    @classmethod
    def card(cls, *children: rx.Component, **props: object) -> rx.Component:
        return custom_auth_card(*children, **props)

    @classmethod
    def heading(cls) -> rx.Component:
        return rx.center(
            custom_brand_icon(),
            rx.heading(
                cls.heading_text(),
                size="6",
                as_="h2",
                text_align="center",
                width="100%",
            ),
            direction="column",
            spacing="5",
            width="100%",
        )
