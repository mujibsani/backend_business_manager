from django.contrib import admin

from .models import LedgerEntry


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "party",
        "party_type",
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
        "customer__name",
        "supplier__name",
        "reference_no",
        "description",
    )

    ordering = (
        "-date",
        "-id",
    )

    date_hierarchy = "date"

    list_per_page = 50

    readonly_fields = (
        "balance",
        "created_at",
        "updated_at",
    )

    fieldsets = (

        (
            "Party Information",
            {
                "fields": (
                    "party_type",
                    "customer",
                    "supplier",
                )
            },
        ),

        (
            "Reference",
            {
                "fields": (
                    "reference_type",
                    "reference_no",
                    "description",
                )
            },
        ),

        (
            "Amount",
            {
                "fields": (
                    "debit",
                    "credit",
                    "balance",
                )
            },
        ),

        (
            "Date",
            {
                "fields": (
                    "date",
                )
            },
        ),

        (
            "System",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),

    )

    def party(self, obj):

        if obj.customer:
            return obj.customer.name

        if obj.supplier:
            return obj.supplier.name

        return "-"

    party.short_description = "Party"