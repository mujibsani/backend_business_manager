from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_no",
        "customer",
        "sales_person",
        "total_amount",
        "paid_amount",
        "due_amount",
        "status",
        "date"
    )

    list_filter = ("status", "date", "sales_person",)
    search_fields = ("invoice_no", "customer__name")

    inlines = [SaleItemInline]

    readonly_fields = ("total_amount", "due_amount", "status")


