from django.contrib import admin
from .models import LedgerEntry


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "party_type",
        "customer",
        "supplier",
        "reference_type",
        "reference_no",
        "debit",
        "credit",
        "balance",
    )

    list_filter = (
        "party_type",
        "reference_type",
        "date",
    )

    search_fields = (
        "reference_no",
        "customer__name",
        "supplier__name",
        "description",
    )

    readonly_fields = (
        "balance",
    )

    ordering = (
        "-date",
        "-id",
    )