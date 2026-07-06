from django.contrib import admin
from .models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    readonly_fields = ("subtotal",)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_no",
        "supplier",
        "total_amount",
        "paid_amount",
        "due_amount",
        "status",
        "date"
    )

    list_filter = ("status", "date")
    search_fields = ("invoice_no", "supplier__name")

    inlines = [PurchaseItemInline]

    readonly_fields = ("total_amount", "due_amount", "status")


