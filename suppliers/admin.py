from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "name",
        "phone",
        "district",
        "opening_balance",
        "opening_balance_type",
        "is_active",
    )

    list_filter = (
        "division",
        "district",
        "opening_balance_type",
        "is_active",
    )

    search_fields = (
        "name",
        "phone",
    )

    ordering = (
        "name",
    )