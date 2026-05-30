"""Navbar component for the app."""

import reflex as rx

from dashboard import styles


def menu_item_icon(icon: str) -> rx.Component:
    return rx.icon(icon, size=20)


def menu_item(text: str, url: str) -> rx.Component:
    """Menu item.

    Args:
        text: The text of the item.
        url: The URL of the item.

    Returns:
        rx.Component: The menu item component.

    """
    # Whether the item is active.
    active = rx.State.router.page.path == url.lower()

    return rx.link(
        rx.hstack(
            rx.match(
                text,
                ("Overview", menu_item_icon("home")),
                ("Transactions", menu_item_icon("table-2")),
                ("Chatbot", menu_item_icon("bot")),
                ("About", menu_item_icon("book-open")),
                ("Profile", menu_item_icon("user")),
                ("Settings", menu_item_icon("settings")),
                menu_item_icon("layout-dashboard"),
            ),
            rx.text(text, size="4", weight="regular"),
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
                        styles.gray_bg_color,
                    ),
                    "color": rx.cond(
                        active,
                        styles.accent_text_color,
                        styles.text_color,
                    ),
                    "opacity": "1",
                },
                "opacity": rx.cond(
                    active,
                    "1",
                    "0.95",
                ),
            },
            align="center",
            border_radius=styles.border_radius,
            width="100%",
            spacing="2",
            padding="0.35em",
        ),
        underline="none",
        href=url,
        width="100%",
    )


def navbar_footer() -> rx.Component:
    """Navbar footer.

    Returns:
        The navbar footer component.

    """
    return rx.hstack(
        rx.spacer(),
        rx.color_mode.button(style={"opacity": "0.8", "scale": "0.95"}),
        justify="start",
        align="center",
        width="100%",
        padding="0.35em",
    )


def menu_button() -> rx.Component:
    from reflex.page import DECORATED_PAGES

    ordered_page_routes = [
        "/",
        "/transactions",
        "/chatbot",
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

    return rx.drawer.root(
        rx.drawer.trigger(
            rx.icon("align-justify"),
        ),
        rx.drawer.overlay(z_index="5"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.hstack(
                        rx.spacer(),
                        rx.drawer.close(rx.icon(tag="x")),
                        justify="end",
                        width="100%",
                    ),
                    rx.divider(),
                    *[
                        menu_item(
                            text=page.get(
                                "title", page["route"].strip("/").capitalize()
                            ),
                            url=page["route"],
                        )
                        for page in ordered_pages
                    ],
                    rx.spacer(),
                    navbar_footer(),
                    spacing="4",
                    width="100%",
                ),
                top="auto",
                left="auto",
                height="100%",
                width="20em",
                padding="1em",
                bg=rx.color("gray", 1),
            ),
            width="100%",
        ),
        direction="right",
    )


from dashboard.components.sidebar import SidebarState

def navbar() -> rx.Component:
    """The navbar.

    Returns:
        The navbar component.

    """
    return rx.el.nav(
        rx.hstack(
            rx.icon(
                "grid-3x3",
                size=24,
                color="white",
                margin_right="1em",
                cursor="pointer",
                display=["none", "none", "block"],
                on_click=SidebarState.toggle_collapse,
            ),
            # The logo.
            rx.image(src="/rxdjango-logo.png", height="2.0em", border_radius="var(--radius-1)"),
            rx.spacer(),
            rx.input(
                rx.input.slot(rx.icon("search", color=rx.color("gray", 11)), padding_left="0"),
                placeholder="Search...",
                size="2",
                width="100%",
                max_width=["120px", "200px", "300px", "400px"],
                radius="medium",
                style={"background_color": rx.color_mode_cond("white", rx.color("gray", 4)), "border": "none"},
            ),
            rx.spacer(),
            rx.flex(
                rx.icon("bell", color="white", size=20, cursor="pointer"),
                rx.icon("message-square-text", color="white", size=20, cursor="pointer"),
                rx.icon("user", color="white", size=20, cursor="pointer"),
                rx.color_mode.button(style={"color": "white", "opacity": "0.9", "scale": "0.95"}),
                spacing="4",
                align="center",
                display=["none", "none", "flex"],
            ),
            rx.box(
                menu_button(),
                display=["block", "block", "none", "none", "none", "none"],
            ),
            align="center",
            width="100%",
            padding_y="0.8em",
            padding_x=["1em", "1em", "1.5em"],
        ),
        display="block",
        position="sticky",
        background_color=rx.color("accent", 9),
        top="0px",
        z_index="10",
        width="100%",
        border_bottom="1px solid rgba(0,0,0,0.1)",
    )
