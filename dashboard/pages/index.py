"""The overview page of the app."""

import datetime

import reflex as rx
from reflex_django.auth import login_required

from .. import styles
from ..components.card import card
from ..components.notification import notification
from ..state.overview import OverviewState
from ..templates import template
from ..views.acquisition_view import acquisition
from ..views.charts import (
    area_toggle,
    orders_chart,
    pie_chart,
    revenue_chart,
    timeframe_select,
    users_chart,
)
from ..views.stats_cards import stats_cards


def _time_data() -> rx.Component:
    return rx.hstack(
        rx.tooltip(
            rx.icon("info", size=20),
            content=f"{(datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%b %d, %Y')} - {datetime.datetime.now().strftime('%b %d, %Y')}",
        ),
        rx.text("Last 30 days", size="4", weight="medium"),
        align="center",
        spacing="2",
        display=["none", "none", "flex"],
    )


def tab_content_header() -> rx.Component:
    return rx.hstack(
        _time_data(),
        area_toggle(),
        align="center",
        width="100%",
        spacing="4",
    )


@login_required
@template(route="/", title="Overview", on_load=OverviewState.load_metrics)
def index() -> rx.Component:
    """The overview page.

    Returns:
        The UI for the overview page.

    """
    return rx.vstack(
        rx.heading(f"Welcome, {OverviewState.welcome_name}", size="7", margin_bottom="0.5em"),
        stats_cards(),
        card(
            rx.hstack(
                tab_content_header(),
                rx.segmented_control.root(
                    rx.segmented_control.item("Users", value="users"),
                    rx.segmented_control.item("Revenue", value="revenue"),
                    rx.segmented_control.item("Orders", value="orders"),
                    margin_bottom="1.5em",
                    default_value="users",
                    on_change=OverviewState.set_selected_tab,
                ),
                width="100%",
                justify="between",
            ),
            rx.match(
                OverviewState.selected_tab,
                ("users", users_chart()),
                ("revenue", revenue_chart()),
                ("orders", orders_chart()),
            ),
        ),
        rx.grid(
            card(
                rx.hstack(
                    rx.hstack(
                        rx.icon("user-round-search", size=20),
                        rx.text("Visitors Analytics", size="4", weight="medium"),
                        align="center",
                        spacing="2",
                    ),
                    timeframe_select(),
                    align="center",
                    width="100%",
                    justify="between",
                ),
                pie_chart(),
            ),
            card(
                rx.hstack(
                    rx.icon("globe", size=20),
                    rx.text("Acquisition Overview", size="4", weight="medium"),
                    align="center",
                    spacing="2",
                    margin_bottom="2.5em",
                ),
                rx.vstack(
                    acquisition(),
                ),
            ),
            gap="1rem",
            grid_template_columns=[
                "1fr",
                "repeat(1, 1fr)",
                "repeat(2, 1fr)",
                "repeat(2, 1fr)",
                "repeat(2, 1fr)",
            ],
            width="100%",
        ),
        spacing="8",
        width="100%",
    )
