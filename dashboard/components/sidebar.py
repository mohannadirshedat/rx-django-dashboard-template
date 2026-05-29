"""Sidebar component for the app."""

import reflex as rx

from .. import styles
from reflex_django.states import DjangoAuthState


class SidebarState(rx.State):
    """The state for the collapsible sidebar."""
    is_collapsed: bool = False

    @rx.event
    def toggle_collapse(self):
        """Toggle the collapsed state of the sidebar."""
        self.is_collapsed = not self.is_collapsed


def sidebar_header() -> rx.Component:
    """Sidebar header.

    Returns:
        The sidebar header component.

    """
    return rx.hstack(
        # The logo.
        rx.image(src="/rxdjango-logo.png", height="2.0em", border_radius="var(--radius-1)"),
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
                rx.cond(
                    ~SidebarState.is_collapsed,
                    rx.text("Log out", size="3", weight="regular", font_family='"Segoe UI Variable", "Segoe UI", "Inter", sans-serif'),
                ),
                align="center",
                width="100%",
                spacing="2",
                padding="0.6em 0.8em",
            ),
            on_click=DjangoAuthState.logout,
            variant="ghost",
            width="100%",
            cursor="pointer",
            style={
                "_hover": {
                    "background_color": rx.color("gray", 4),
                    "color": rx.color("gray", 12),
                },
                "color": rx.color("gray", 11),
                "border_radius": "4px",
            },
        ),
        rx.fragment(),
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
    active = rx.State.router.page.path == url.lower()

    return rx.link(
        rx.hstack(
            rx.cond(
                active,
                rx.box(
                    width="3px",
                    height="18px",
                    bg=rx.color("accent", 9),
                    position="absolute",
                    left="2px",
                    border_radius="9999px",
                ),
                rx.fragment(),
            ),
            rx.match(
                text,
                ("Overview", sidebar_item_icon("home")),
                ("Transactions", sidebar_item_icon("table-2")),
                ("About", sidebar_item_icon("book-open")),
                ("Profile", sidebar_item_icon("user")),
                ("Settings", sidebar_item_icon("settings")),
                sidebar_item_icon("layout-dashboard"),
            ),
            rx.cond(
                ~SidebarState.is_collapsed,
                rx.text(
                    text,
                    size="3",
                    weight=rx.cond(active, "semibold", "regular"),
                    font_family='"Segoe UI Variable", "Segoe UI", "Inter", sans-serif',
                ),
            ),
            color=rx.cond(
                active,
                rx.color("gray", 12),
                rx.color("gray", 11),
            ),
            style={
                "_hover": {
                    "background_color": rx.cond(
                        active,
                        rx.color("gray", 5),
                        rx.color("gray", 4),
                    ),
                    "color": rx.color("gray", 12),
                    "opacity": "1",
                },
                "background_color": rx.cond(
                    active,
                    rx.color("gray", 4),
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
            border_radius="4px",
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
        "/transactions",
        "/about",
        "/profile",
        "/settings",
    ]

    pages = [
        page_dict
        for page_list in DECORATED_PAGES.values()
        for _, page_dict in page_list
        if page_dict.get("route") in ordered_page_routes
    ]

    ordered_pages = sorted(
        pages,
        key=lambda page: ordered_page_routes.index(page["route"]),
    )

    width_val = rx.cond(SidebarState.is_collapsed, "4.5em", styles.sidebar_content_width)

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
            justify="start",
            align="start",
            width=width_val,
            height="calc(100vh - 60px)",
            padding_x=rx.cond(SidebarState.is_collapsed, "0.5em", ["1em", "1em", "0.7em"]),
            padding_y="1.5em",
            transition="width 0.2s ease-in-out, padding 0.2s ease-in-out",
        ),
        display=["none", "none", "flex", "flex", "flex", "flex"],
        max_width=width_val,
        width=width_val,
        height="100%",
        position="sticky",
        justify="start",
        top="60px",
        left="0px",
        flex="none",
        bg=rx.color_mode_cond(rx.color("gray", 2), rx.color("gray", 3)),
        border_right=f"1px solid {rx.color('gray', 4)}",
        transition="width 0.2s ease-in-out, max-width 0.2s ease-in-out",
    )
