from django.db import models

from core.models import TimeStampedModel


class ExpenseCategory(TimeStampedModel):
    """
    Expense Categories
    Example:
        Fuel
        Transport
        Salary
        Electricity
        Internet
        Office Rent
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name


class Expense(TimeStampedModel):
    """
    Business Expense
    """

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="expenses",
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    date = models.DateField()

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.category.name} - {self.amount}"