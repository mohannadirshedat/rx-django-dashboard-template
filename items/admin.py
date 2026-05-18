from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("name", "payment", "date", "status")
    list_filter = ("status", "date")
    search_fields = ("name",)
