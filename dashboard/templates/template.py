"""Shared sidebar+navbar layout decorator for dashboard pages.

This is the dashboard's custom ``@template`` decorator. It wraps a page body
in the dashboard chrome (navbar + sidebar) and registers the route with
Reflex via :func:`reflex_django.page` so the page is bucketed into
``DECORATED_PAGES[reflex_mount().app_name]`` (avoids the
``dispatch is not a function`` class of errors that result when pages land
in ``DECORATED_PAGES[""]``).

When ``login_required=True``, the template wraps the rendered component with
:class:`~reflex_django.auth.state.DjangoAuthState` snapshot guards *before*
the page is registered with Reflex. Stacking ``@login_required`` on top of
``@template`` does not work because ``@template`` registers the page first
and the outer ``@login_required`` wrapper is discarded; use the keyword
argument instead.
"""

from __future__ import annotations

import functools
from typing import Callable

import reflex as rx
from reflex_django.pages.decorators import page
from reflex_django.states import DjangoAuthState

from .. import styles
from ..components.navbar import navbar
from ..components.sidebar import sidebar

default_meta = [
    {
        "name": "viewport",
        "content": "width=device-width, shrink-to-fit=no, initial-scale=1",
    },
]


def menu_item_link(text, href):
    return rx.menu.item(
        rx.link(
            text,
            href=href,
            width="100%",
            color="inherit",
        ),
        _hover={
            "color": styles.accent_color,
            "background_color": styles.accent_text_color,
        },
    )


class ThemeState(rx.State):
    """Reflex state for the user-selectable theme tokens."""

    accent_color: str = "blue"
    gray_color: str = "slate"
    radius: str = "medium"
    scaling: str = "100%"

    @rx.event
    def set_scaling(self, value: str):
        self.scaling = value

    @rx.event
    def set_radius(self, value: str):
        self.radius = value

    @rx.event
    def set_accent_color(self, value: str):
        self.accent_color = value

    @rx.event
    def set_gray_color(self, value: str):
        self.gray_color = value


ALL_PAGES: list[dict] = []


def template(
    route: str | None = None,
    title: str | None = None,
    description: str | None = None,
    meta: list[dict[str, str]] | None = None,
    script_tags: list[rx.Component] | None = None,
    on_load: rx.event.EventType[()] | None = None,
    login_required: bool = False,
) -> Callable[[Callable[[], rx.Component]], rx.Component]:
    """Wrap a page body in the dashboard shell and register it with Reflex.

    Args:
        route: Client-side route (for example ``"/"`` or ``"/profile"``).
        title: Browser tab title (also used by the sidebar).
        description: Page description meta tag.
        meta: Extra meta tags merged with the dashboard defaults.
        script_tags: Optional ``<script>`` tags forwarded to Reflex.
        on_load: Event handler(s) to run when the route is visited.
        login_required: Require the visitor to be authenticated. Anonymous
            visitors are redirected to ``REFLEX_DJANGO_AUTH["LOGIN_URL"]``
            (default ``/login``). Set this on protected routes instead of
            stacking ``@login_required`` on top — the outer decorator never
            reaches the Reflex page registry because ``@template`` registers
            the route first.

    Returns:
        A decorator that registers the page via :func:`reflex_django.page`.
    """
    all_meta = [*default_meta, *(meta or [])]
    page_on_load = (
        None if on_load is None else (on_load if isinstance(on_load, list) else [on_load])
    )

    def decorator(page_content: Callable[[], rx.Component]) -> rx.Component:
        def dashboard_body() -> rx.Component:
            return rx.vstack(
                navbar(),
                rx.flex(
                    sidebar(),
                    rx.flex(
                        rx.vstack(
                            page_content(),
                            width="100%",
                            **styles.template_content_style,
                        ),
                        width="100%",
                        **styles.template_page_style,
                        max_width=[
                            "100%",
                            "100%",
                            "100%",
                            "100%",
                            "100%",
                            styles.max_width,
                        ],
                    ),
                    flex_direction=[
                        "column",
                        "column",
                        "row",
                        "row",
                        "row",
                        "row",
                    ],
                    width="100%",
                    margin="auto",
                    position="relative",
                ),
                width="100%",
                spacing="0",
            )

        def gated_body() -> rx.Component:
            return rx.cond(
                DjangoAuthState.is_hydrated & DjangoAuthState.is_authenticated,
                dashboard_body(),
                rx.center(
                    rx.text(
                        "Loading...",
                        on_mount=DjangoAuthState.redirect_to_login,
                    ),
                    min_height="100vh",
                    width="100%",
                ),
            )

        page_kwargs: dict = {
            "route": route,
            "title": title,
            "meta": all_meta,
        }
        if description is not None:
            page_kwargs["description"] = description
        if script_tags is not None:
            page_kwargs["script_tags"] = script_tags
        if page_on_load is not None:
            page_kwargs["on_load"] = page_on_load

        @functools.wraps(page_content)
        def theme_wrap():
            return rx.theme(
                gated_body() if login_required else dashboard_body(),
                has_background=True,
                accent_color=ThemeState.accent_color,
                gray_color=ThemeState.gray_color,
                radius=ThemeState.radius,
                scaling=ThemeState.scaling,
            )

        decorated = page(**page_kwargs)(theme_wrap)

        ALL_PAGES.append(
            {"route": route} | ({"title": title} if title is not None else {})
        )

        return decorated

    return decorator
