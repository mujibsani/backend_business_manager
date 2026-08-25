from django.contrib import admin

from .models import (
    SalesReturn,
    SalesReturnItem,
)


class SalesReturnItemInline(
    admin.TabularInline
):

    model = SalesReturnItem

    extra = 0

    readonly_fields = (
        "subtotal",
    )


@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):

    list_display = (
        "return_no",
        "sale",
        "customer",
        "date",
        "total_amount",
        "refund_amount",
        "status",
        "created_by",
    )

    list_filter = (
        "status",
        "date",
    )

    search_fields = (
        "return_no",
        "sale__invoice_no",
        "customer__name",
    )

    readonly_fields = (
        "return_no",
        "total_amount",
        "created_by",
        "created_at",
        "updated_at",
    )

    inlines = [
        SalesReturnItemInline,
    ]