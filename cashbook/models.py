from django.db import models
from core.models import TimeStampedModel


class CashbookEntry(TimeStampedModel):

    ENTRY_TYPE = (
        ("IN", "Cash In"),
        ("OUT", "Cash Out"),
    )

    SOURCE_TYPE = (
        ("SALE", "Sale"),
        ("PURCHASE", "Purchase"),
        ("EXPENSE", "Expense"),
        ("OTHER", "Other"),
    )

    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE, default="OTHER")

    amount = models.DecimalField(max_digits=14, decimal_places=2)

    reference = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255, blank=True)

    date = models.DateField()

    def __str__(self):
        return f"{self.entry_type} - {self.amount}"