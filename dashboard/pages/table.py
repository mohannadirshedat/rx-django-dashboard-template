"""The table page."""

import reflex as rx
from reflex_django.auth import login_required

from ..state.transactions import TransactionState
from ..templates import template
from ..views.table import main_table


@login_required
@template(route="/transactions", title="Transactions", on_load=TransactionState.load_transactions)
def table() -> rx.Component:
    """The table page.

    Returns:
        The UI for the table page.

    """
    return rx.vstack(
        rx.heading("Table", size="5"),
        main_table(),
        spacing="8",
        width="100%",
    )
