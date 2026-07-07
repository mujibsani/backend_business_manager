from django.contrib import admin

from .models import ExpenseCategory, Expense


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "description",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    ordering = (
        "name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 25


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "category",
        "amount",
        "date",
        "description",
        "created_at",
    )

    search_fields = (
        "description",
        "category__name",
    )

    list_filter = (
        "category",
        "date",
        "created_at",
    )

    autocomplete_fields = (
        "category",
    )

    list_select_related = (
        "category",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "date"

    ordering = (
        "-date",
        "-id",
    )

    list_per_page = 25