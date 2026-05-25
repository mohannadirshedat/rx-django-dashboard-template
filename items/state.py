"""Reflex state for the transactions table page."""

import math
from datetime import date
from decimal import Decimal, InvalidOperation

import reflex as rx
from django.db.models import Q
from reflex_django.auth.decorators import login_required
from reflex_django.state import AppState

from items.models import Transaction, TransactionStatus
from items.serializers import TransactionSerializer

STATUS_VALUES = {choice.value for choice in TransactionStatus}


class TransactionState(AppState):
    transactions: list[dict] = []
    error: str = ""

    page: int = 1
    page_size: int = 12
    page_count: int = 1
    search_query: str = ""

    sort_reverse: bool = False
    sort_field: str = "date"

    modal_open: bool = False
    editing_id: int = -1
    name: str = ""
    payment: str = ""
    date: str = ""
    status: str = TransactionStatus.PENDING.value

    delete_dialog_open: bool = False
    deleting_id: int = -1

    def _filtered_qs(self):
        prefix = "-" if self.sort_reverse else ""
        qs = Transaction.objects.all().order_by(f"{prefix}{self.sort_field}")
        q = self.search_query.strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(status__icontains=q))
        return qs

    def _reset_form(self) -> None:
        self.name = ""
        self.payment = ""
        self.date = ""
        self.status = TransactionStatus.PENDING.value
        self.editing_id = -1

    def _validate(self) -> str | None:
        if not self.name.strip():
            return "Name is required."
        try:
            amount = Decimal(self.payment)
            if amount < 0:
                return "Payment must be non-negative."
        except (InvalidOperation, TypeError):
            return "Invalid payment amount."
        if not self.date.strip():
            return "Date is required."
        try:
            date.fromisoformat(self.date)
        except ValueError:
            return "Invalid date."
        if self.status not in STATUS_VALUES:
            return "Invalid status."
        return None

    @rx.event
    @login_required
    async def load_transactions(self):
        await self.refresh_django_user_fields()
        self.error = ""
        try:
            qs = self._filtered_qs()
            total = await qs.acount()
            self.page_count = max(1, math.ceil(total / self.page_size))
            if self.page > self.page_count:
                self.page = self.page_count
            if self.page < 1:
                self.page = 1
            start = (self.page - 1) * self.page_size
            page_qs = qs[start : start + self.page_size]
            self.transactions = await TransactionSerializer(page_qs, many=True).adata()
        except Exception as exc:
            self.error = str(exc)

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value
        self.page = 1

    @rx.event
    def set_name(self, value: str):
        self.name = value

    @rx.event
    def set_payment(self, value: str):
        self.payment = value

    @rx.event
    def set_date(self, value: str):
        self.date = value

    @rx.event
    def set_status(self, value: str):
        self.status = value

    @rx.event
    @login_required
    async def apply_search(self):
        await self.load_transactions()

    @rx.event
    @login_required
    async def clear_search(self):
        self.search_query = ""
        self.page = 1
        await self.load_transactions()

    @rx.event
    @login_required
    async def toggle_sort_reverse(self):
        self.sort_reverse = not self.sort_reverse
        await self.load_transactions()

    @rx.event
    @login_required
    async def set_sort_field(self, value: str):
        self.sort_field = value
        self.page = 1
        await self.load_transactions()

    @rx.event
    @login_required
    async def prev_page(self):
        if self.page > 1:
            self.page -= 1
            await self.load_transactions()

    @rx.event
    @login_required
    async def next_page(self):
        if self.page < self.page_count:
            self.page += 1
            await self.load_transactions()

    @rx.event
    @login_required
    async def first_page(self):
        self.page = 1
        await self.load_transactions()

    @rx.event
    @login_required
    async def last_page(self):
        self.page = self.page_count
        await self.load_transactions()

    @rx.event
    @login_required
    def open_create_modal(self):
        self.error = ""
        self._reset_form()
        self.modal_open = True

    @rx.event
    @login_required
    async def open_edit_modal(self, transaction_id: int):
        self.error = ""
        try:
            transaction = await Transaction.objects.aget(pk=transaction_id)
            row = await TransactionSerializer(transaction).adata()
            self.editing_id = int(row["id"])
            self.name = row["name"]
            self.payment = str(row["payment"])
            self.date = row["date"]
            self.status = row["status"]
            self.modal_open = True
        except Exception as exc:
            self.error = str(exc)

    @rx.event
    def set_modal_open(self, open: bool):
        self.modal_open = open
        if not open:
            self._reset_form()

    @rx.event
    @login_required
    def close_modal(self):
        self.modal_open = False
        self._reset_form()

    @rx.event
    @login_required
    async def save_transaction(self):
        self.error = ""
        err = self._validate()
        if err:
            self.error = err
            return
        data = {
            "name": self.name.strip(),
            "payment": Decimal(self.payment),
            "date": date.fromisoformat(self.date),
            "status": self.status,
        }
        try:
            if self.editing_id >= 0:
                transaction = await Transaction.objects.aget(pk=self.editing_id)
                for key, val in data.items():
                    setattr(transaction, key, val)
                await transaction.asave()
                message = "Transaction updated."
            else:
                await Transaction.objects.acreate(**data)
                message = "Transaction created."
            self.modal_open = False
            self._reset_form()
            await self.load_transactions()
            return rx.toast.success(message, position="top-center")
        except Exception as exc:
            self.error = str(exc)

    @rx.event
    @login_required
    def open_delete_dialog(self, transaction_id: int):
        self.deleting_id = transaction_id
        self.delete_dialog_open = True

    @rx.event
    def set_delete_dialog_open(self, open: bool):
        self.delete_dialog_open = open
        if not open:
            self.deleting_id = -1

    @rx.event
    @login_required
    def close_delete_dialog(self):
        self.delete_dialog_open = False
        self.deleting_id = -1

    @rx.event
    @login_required
    async def delete_transaction(self):
        if self.deleting_id < 0:
            return
        self.error = ""
        try:
            transaction = await Transaction.objects.aget(pk=self.deleting_id)
            await transaction.adelete()
            self.delete_dialog_open = False
            self.deleting_id = -1
            await self.load_transactions()
            return rx.toast.success("Transaction deleted.", position="top-center")
        except Exception as exc:
            self.error = str(exc)
