import reflex as rx

from ..components.status_badge import status_badge
from ..state.transactions import TransactionState


def _header_cell(text: str, icon: str) -> rx.Component:
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )


def _show_row(row: dict, index: int) -> rx.Component:
    bg_color = rx.cond(
        index % 2 == 0,
        rx.color("gray", 1),
        rx.color("accent", 2),
    )
    hover_color = rx.cond(
        index % 2 == 0,
        rx.color("gray", 3),
        rx.color("accent", 3),
    )
    return rx.table.row(
        rx.table.row_header_cell(row["name"]),
        rx.table.cell(rx.text("$", row["payment"])),
        rx.table.cell(row["date"]),
        rx.table.cell(status_badge(row["status"])),
        rx.table.cell(
            rx.hstack(
                rx.icon_button(
                    rx.icon("pencil", size=16),
                    size="1",
                    variant="soft",
                    on_click=TransactionState.open_edit_modal(row["id"]),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=16),
                    size="1",
                    variant="soft",
                    color_scheme="red",
                    on_click=TransactionState.open_delete_dialog(row["id"]),
                ),
                spacing="2",
            ),
        ),
        style={"_hover": {"bg": hover_color}, "bg": bg_color},
        align="center",
    )


def _pagination_view() -> rx.Component:
    return rx.hstack(
        rx.text(
            "Page ",
            rx.code(TransactionState.page),
            " of ",
            rx.code(TransactionState.page_count),
            justify="end",
        ),
        rx.hstack(
            rx.icon_button(
                rx.icon("chevrons-left", size=18),
                on_click=TransactionState.first_page,
                opacity=rx.cond(TransactionState.page == 1, 0.6, 1),
                color_scheme=rx.cond(TransactionState.page == 1, "gray", "accent"),
                variant="soft",
            ),
            rx.icon_button(
                rx.icon("chevron-left", size=18),
                on_click=TransactionState.prev_page,
                opacity=rx.cond(TransactionState.page == 1, 0.6, 1),
                color_scheme=rx.cond(TransactionState.page == 1, "gray", "accent"),
                variant="soft",
            ),
            rx.icon_button(
                rx.icon("chevron-right", size=18),
                on_click=TransactionState.next_page,
                opacity=rx.cond(
                    TransactionState.page == TransactionState.page_count,
                    0.6,
                    1,
                ),
                color_scheme=rx.cond(
                    TransactionState.page == TransactionState.page_count,
                    "gray",
                    "accent",
                ),
                variant="soft",
            ),
            rx.icon_button(
                rx.icon("chevrons-right", size=18),
                on_click=TransactionState.last_page,
                opacity=rx.cond(
                    TransactionState.page == TransactionState.page_count,
                    0.6,
                    1,
                ),
                color_scheme=rx.cond(
                    TransactionState.page == TransactionState.page_count,
                    "gray",
                    "accent",
                ),
                variant="soft",
            ),
            align="center",
            spacing="2",
            justify="end",
        ),
        spacing="5",
        margin_top="1em",
        align="center",
        width="100%",
        justify="end",
    )


def _transaction_form_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    TransactionState.editing_id >= 0,
                    "Edit transaction",
                    "New transaction",
                ),
            ),
            rx.cond(
                TransactionState.error != "",
                rx.callout(
                    TransactionState.error,
                    color_scheme="red",
                    margin_bottom="1em",
                ),
            ),
            rx.vstack(
                rx.text("Name", size="2", weight="medium"),
                rx.input(
                    value=TransactionState.name,
                    on_change=TransactionState.set_name,
                    placeholder="Transaction name",
                    width="100%",
                ),
                rx.text("Payment", size="2", weight="medium"),
                rx.input(
                    value=TransactionState.payment,
                    on_change=TransactionState.set_payment,
                    placeholder="0.00",
                    type="number",
                    width="100%",
                ),
                rx.text("Date", size="2", weight="medium"),
                rx.input(
                    value=TransactionState.date,
                    on_change=TransactionState.set_date,
                    type="date",
                    width="100%",
                ),
                rx.text("Status", size="2", weight="medium"),
                rx.select(
                    ["Pending", "Completed", "Canceled"],
                    value=TransactionState.status,
                    on_change=TransactionState.set_status,
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button("Cancel", variant="soft", color_scheme="gray"),
                ),
                rx.button(
                    "Save",
                    on_click=TransactionState.save_transaction,
                ),
                spacing="3",
                justify="end",
                width="100%",
                margin_top="1em",
            ),
            size="3",
        ),
        open=TransactionState.modal_open,
        on_open_change=TransactionState.set_modal_open,
    )


def _delete_confirm_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Delete transaction?"),
            rx.alert_dialog.description(
                "This action cannot be undone. The transaction will be permanently removed.",
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Cancel", variant="soft", color_scheme="gray"),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Delete",
                        color_scheme="red",
                        on_click=TransactionState.delete_transaction,
                    ),
                ),
                spacing="3",
                justify="end",
                margin_top="1em",
            ),
            max_width="450px",
        ),
        open=TransactionState.delete_dialog_open,
        on_open_change=TransactionState.set_delete_dialog_open,
    )


def main_table() -> rx.Component:
    return rx.fragment(
        rx.box(
            rx.flex(
                rx.flex(
                    rx.cond(
                        TransactionState.sort_reverse,
                        rx.icon(
                            "arrow-down-z-a",
                            size=28,
                            stroke_width=1.5,
                            cursor="pointer",
                            flex_shrink="0",
                            on_click=TransactionState.toggle_sort_reverse,
                        ),
                        rx.icon(
                            "arrow-down-a-z",
                            size=28,
                            stroke_width=1.5,
                            cursor="pointer",
                            flex_shrink="0",
                            on_click=TransactionState.toggle_sort_reverse,
                        ),
                    ),
                    rx.select(
                        ["name", "payment", "date", "status"],
                        placeholder="Sort By: Name",
                        size="3",
                        on_change=TransactionState.set_sort_field,
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("search")),
                        rx.input.slot(
                            rx.icon("x"),
                            justify="end",
                            cursor="pointer",
                            on_click=TransactionState.clear_search,
                            display=rx.cond(
                                TransactionState.search_query != "",
                                "flex",
                                "none",
                            ),
                        ),
                        value=TransactionState.search_query,
                        placeholder="Search here...",
                        size="3",
                        max_width=["150px", "150px", "200px", "250px"],
                        width="100%",
                        variant="surface",
                        color_scheme="gray",
                        on_change=TransactionState.set_search_query,
                    ),
                    rx.button(
                        "Search",
                        size="3",
                        variant="soft",
                        on_click=TransactionState.apply_search,
                    ),
                    rx.button(
                        rx.icon("plus", size=18),
                        "Add",
                        size="3",
                        on_click=TransactionState.open_create_modal,
                    ),
                    align="center",
                    justify="end",
                    spacing="3",
                ),
                rx.button(
                    rx.icon("arrow-down-to-line", size=20),
                    "Export",
                    size="3",
                    variant="surface",
                    display=["none", "none", "none", "flex"],
                    on_click=rx.download(url="/items.csv"),
                ),
                spacing="3",
                justify="between",
                wrap="wrap",
                width="100%",
                padding_bottom="1em",
            ),
            rx.cond(
                TransactionState.error != "",
                rx.cond(
                    TransactionState.modal_open,
                    rx.fragment(),
                    rx.callout(
                        TransactionState.error,
                        color_scheme="red",
                        margin_bottom="1em",
                    ),
                ),
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        _header_cell("Name", "user"),
                        _header_cell("Payment", "dollar-sign"),
                        _header_cell("Date", "calendar"),
                        _header_cell("Status", "notebook-pen"),
                        _header_cell("Actions", "settings"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        TransactionState.transactions,
                        lambda row, index: _show_row(row, index),
                    )
                ),
                variant="surface",
                size="3",
                width="100%",
            ),
            _pagination_view(),
            width="100%",
        ),
        _transaction_form_modal(),
        _delete_confirm_dialog(),
    )
