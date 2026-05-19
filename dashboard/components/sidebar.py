"""Sidebar component for the app."""

import reflex as rx

from .. import styles
from reflex_django.auth.state import DjangoAuthState


def sidebar_header() -> rx.Component:
    """Sidebar header.

    Returns:
        The sidebar header component.

    """
    return rx.hstack(
        # The logo.
        rx.color_mode_cond(
            rx.image(src="/reflex_black.svg", height="1.5em"),
            rx.image(src="/reflex_white.svg", height="1.5em"),
        ),
        rx.spacer(),
        align="center",
        width="100%",
        padding="0.35em",
        margin_bottom="1em",
    )


def sidebar_logout_item() -> rx.Component:
    """Log out control (visible when signed in)."""
    return rx.cond(
        DjangoAuthState.is_authenticated,
        rx.button(
            rx.hstack(
                sidebar_item_icon("log-out"),
                rx.text("Log out", size="3", weight="regular"),
                color=styles.text_color,
                align="center",
                border_radius=styles.border_radius,
                width="100%",
                spacing="2",
                padding="0.35em",
            ),
            on_click=DjangoAuthState.logout,
            variant="ghost",
            width="100%",
            cursor="pointer",
            style={
                "_hover": {
                    "background_color": styles.gray_bg_color,
                    "color": styles.text_color,
                },
            },
        ),
        rx.fragment(),
    )


def sidebar_footer() -> rx.Component:
    """Sidebar footer.

    Returns:
        The sidebar footer component.

    """
    return rx.hstack(
        rx.link(
            rx.text("Docs", size="3"),
            href="https://reflex.dev/docs/getting-started/introduction/",
            color_scheme="gray",
            underline="none",
        ),
        rx.link(
            rx.text("Blog", size="3"),
            href="https://reflex.dev/blog/",
            color_scheme="gray",
            underline="none",
        ),
        rx.spacer(),
        rx.color_mode.button(style={"opacity": "0.8", "scale": "0.95"}),
        justify="start",
        align="center",
        width="100%",
        padding="0.35em",
    )


def sidebar_item_icon(icon: str) -> rx.Component:
    return rx.icon(icon, size=18)


def sidebar_item(text: str, url: str) -> rx.Component:
    """Sidebar item.

    Args:
        text: The text of the item.
        url: The URL of the item.

    Returns:
        rx.Component: The sidebar item component.

    """
    # Whether the item is active.
    active = (rx.State.router.page.path == url.lower()) | (
        (rx.State.router.page.path == "/") & text == "Overview"
    )

    return rx.link(
        rx.hstack(
            rx.cond(
                active,
                rx.box(
                    width="4px",
                    height="20px",
                    background_color=styles.accent_text_color,
                    border_radius="4px",
                    position="absolute",
                    left="0px",
                ),
                rx.fragment(),
            ),
            rx.match(
                text,
                ("Overview", sidebar_item_icon("home")),
                ("Table", sidebar_item_icon("table-2")),
                ("About", sidebar_item_icon("book-open")),
                ("Profile", sidebar_item_icon("user")),
                ("Settings", sidebar_item_icon("settings")),
                sidebar_item_icon("layout-dashboard"),
            ),
            rx.text(text, size="3", weight="regular"),
            color=rx.cond(
                active,
                styles.accent_text_color,
                styles.text_color,
            ),
            style={
                "_hover": {
                    "background_color": rx.cond(
                        active,
                        styles.accent_bg_color,
                        rx.color("gray", 3),
                    ),
                    "color": rx.cond(
                        active,
                        styles.accent_text_color,
                        styles.text_color,
                    ),
                    "opacity": "1",
                },
                "background_color": rx.cond(
                    active,
                    styles.accent_bg_color,
                    "transparent",
                ),
                "opacity": rx.cond(
                    active,
                    "1",
                    "0.95",
                ),
                "position": "relative",
            },
            align="center",
            border_radius="6px",
            width="100%",
            spacing="2",
            padding="0.6em 0.8em",
        ),
        underline="none",
        href=url,
        width="100%",
    )


def sidebar() -> rx.Component:
    """The sidebar.

    Returns:
        The sidebar component.
    """
    from reflex.page import DECORATED_PAGES

    ordered_page_routes = [
        "/",
        "/table",
        "/about",
        "/profile",
        "/settings",
    ]

    pages = [
        page_dict
        for page_list in DECORATED_PAGES.values()
        for _, page_dict in page_list
    ]

    ordered_pages = sorted(
        pages,
        key=lambda page: (
            ordered_page_routes.index(page["route"])
            if page["route"] in ordered_page_routes
            else len(ordered_page_routes)
        ),
    )

    return rx.flex(
        rx.vstack(
            rx.vstack(
                *[
                    sidebar_item(
                        text=page.get("title", page["route"].strip("/").capitalize()),
                        url=page["route"],
                    )
                    for page in ordered_pages
                ],
                spacing="1",
                width="100%",
            ),
            rx.spacer(),
            sidebar_logout_item(),
            sidebar_footer(),
            justify="start",
            align="start",
            width=styles.sidebar_content_width,
            height="calc(100vh - 60px)",
            padding_x=["1em", "1em", "0.7em"],
            padding_y="1.5em",
        ),
        display=["none", "none", "flex", "flex", "flex", "flex"],
        max_width=styles.sidebar_content_width,
        width="auto",
        height="100%",
        position="sticky",
        justify="start",
        top="60px",
        left="0px",
        flex="none",
        bg="transparent",
    )
