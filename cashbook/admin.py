from django.contrib import admin

from .models import CashbookEntry


@admin.register(CashbookEntry)
class CashbookAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "entry_type",
        "source_type",
        "amount",
        "reference",
        "description",
    )

    list_filter = (
        "entry_type",
        "source_type",
        "date",
    )

    search_fields = (
        "reference",
        "description",
    )

    readonly_fields = (
        "date",
        "entry_type",
        "source_type",
        "amount",
        "reference",
        "description",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-date",
        "-id",
    )

    list_per_page = 25

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False