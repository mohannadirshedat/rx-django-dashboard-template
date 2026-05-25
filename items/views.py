"""Reflex pages for the items app (auto-discovered by reflex-django)."""

import reflex as rx

from dashboard.templates import template
from items.components.table import main_table
from items.state import TransactionState


@template(
    route="/transactions",
    title="Transactions",
    on_load=TransactionState.load_transactions,
    login_required=True,
)
def transactions() -> rx.Component:
    """Render the transactions table page."""
    return rx.vstack(
        rx.heading("Table", size="5"),
        main_table(),
        spacing="8",
        width="100%",
    )
