from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "payment_no",
        "payment_type",
        "customer",
        "supplier",
        "amount",
        "payment_method",
        "status",
        "payment_date",
        "received_by",
    )

    list_filter = (
        "payment_type",
        "payment_method",
        "status",
        "payment_date",
    )

    search_fields = (
        "payment_no",
        "reference_no",
        "transaction_id",
        "customer__name",
        "supplier__name",
    )

    autocomplete_fields = (
        "customer",
        "supplier",
        "sale",
        "purchase",
        "received_by",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-payment_date",
        "-id",
    )