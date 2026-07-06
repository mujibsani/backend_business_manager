from django.db import models
from core.models import TimeStampedModel


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Expense(TimeStampedModel):

    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT)

    amount = models.DecimalField(max_digits=14, decimal_places=2)

    date = models.DateField()

    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount}"

    def save(self, *args, **kwargs):

        from cashbook.models import CashbookEntry

        super().save(*args, **kwargs)

        # AUTO CREATE CASHBOOK ENTRY
        CashbookEntry.objects.create(
            entry_type="OUT",
            source_type="EXPENSE",
            amount=self.amount,
            reference=f"EXP-{self.id}",
            description=self.description
        )