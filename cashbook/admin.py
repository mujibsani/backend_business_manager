from django.contrib import admin
from .models import CashbookEntry, TimeStampedModel


@admin.register(CashbookEntry)
class CashbookAdmin(admin.ModelAdmin):

    list_display = (
        "date",
        "entry_type",
        "amount",
        "description"
    )

    list_filter = ("entry_type", "date")
    search_fields = ("description",)

    readonly_fields = ("date", "entry_type", "amount", "description")

    def has_add_permission(self, request):
        return False