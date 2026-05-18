import reflex as rx
from reflex.components.radix.themes.base import LiteralAccentColor

from .. import styles
from ..state.overview import OverviewState


def stats_card(
    stat_name: str,
    value,
    prev_value,
    icon: str,
    icon_color: LiteralAccentColor,
    extra_char: str = "",
) -> rx.Component:
    is_increase = value > prev_value
    percentage = rx.cond(
        prev_value != 0,
        (value - prev_value) / prev_value * 100,
        rx.cond(value == 0, 0, 100),
    )
    arrow_icon = rx.cond(is_increase, "trending-up", "trending-down")
    arrow_color = rx.cond(is_increase, "grass", "tomato")
    change_label = rx.cond(is_increase, "increase", "decrease")

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(
                    rx.icon(tag=icon, size=34),
                    color_scheme=icon_color,
                    radius="full",
                    padding="0.7rem",
                ),
                rx.vstack(
                    rx.heading(
                        rx.hstack(
                            rx.cond(
                                extra_char != "",
                                rx.text(extra_char),
                                rx.fragment(),
                            ),
                            rx.text(value),
                            spacing="1",
                            align="center",
                        ),
                        size="6",
                        weight="bold",
                    ),
                    rx.text(stat_name, size="4", weight="medium"),
                    spacing="1",
                    height="100%",
                    align_items="start",
                    width="100%",
                ),
                height="100%",
                spacing="4",
                align="center",
                width="100%",
            ),
            rx.hstack(
                rx.hstack(
                    rx.icon(
                        tag=arrow_icon,
                        size=24,
                        color=rx.color(arrow_color, 9),
                    ),
                    rx.text(
                        percentage,
                        "%",
                        size="3",
                        color=rx.color(arrow_color, 9),
                        weight="medium",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    change_label,
                    " from last month",
                    size="2",
                    color=rx.color("gray", 10),
                ),
                align="center",
                width="100%",
            ),
            spacing="3",
        ),
        size="3",
        width="100%",
        box_shadow=styles.box_shadow_style,
    )


def stats_cards() -> rx.Component:
    return rx.grid(
        stats_card(
            stat_name="Users",
            value=OverviewState.kpi_users,
            prev_value=OverviewState.kpi_users_prev,
            icon="users",
            icon_color="blue",
        ),
        stats_card(
            stat_name="Revenue",
            value=OverviewState.kpi_revenue,
            prev_value=OverviewState.kpi_revenue_prev,
            icon="dollar-sign",
            icon_color="green",
            extra_char="$",
        ),
        stats_card(
            stat_name="Orders",
            value=OverviewState.kpi_orders,
            prev_value=OverviewState.kpi_orders_prev,
            icon="shopping-cart",
            icon_color="purple",
        ),
        gap="1rem",
        grid_template_columns=[
            "1fr",
            "repeat(1, 1fr)",
            "repeat(2, 1fr)",
            "repeat(3, 1fr)",
            "repeat(3, 1fr)",
        ],
        width="100%",
    )
