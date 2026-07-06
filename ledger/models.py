from decimal import Decimal

from django.db import models
from core.models import TimeStampedModel
from customers.models import Customer
from suppliers.models import Supplier


class LedgerEntry(TimeStampedModel):

    PARTY_TYPE = (
        ("CUSTOMER", "Customer"),
        ("SUPPLIER", "Supplier"),
    )

    REFERENCE_TYPE = (
        ("SALE", "Sale"),
        ("PURCHASE", "Purchase"),
        ("PAYMENT", "Payment"),
        ("ADJUSTMENT", "Adjustment"),
    )

    party_type = models.CharField(
        max_length=20,
        choices=PARTY_TYPE
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ledger_entries"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ledger_entries"
    )

    reference_type = models.CharField(
        max_length=20,
        choices=REFERENCE_TYPE
    )

    reference_no = models.CharField(
        max_length=100,
        blank=True
    )

    debit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    credit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    date = models.DateField()

    class Meta:
        ordering = ["date", "id"]

    def clean(self):
        if self.party_type == "CUSTOMER" and not self.customer:
            raise ValueError("Customer is required.")

        if self.party_type == "SUPPLIER" and not self.supplier:
            raise ValueError("Supplier is required.")

    def save(self, *args, **kwargs):

        previous_balance = Decimal("0.00")

        if self.party_type == "CUSTOMER":

            last = LedgerEntry.objects.filter(
                customer=self.customer
            ).exclude(pk=self.pk).order_by("-date", "-id").first()

        else:

            last = LedgerEntry.objects.filter(
                supplier=self.supplier
            ).exclude(pk=self.pk).order_by("-date", "-id").first()

        if last:
            previous_balance = last.balance

        self.balance = previous_balance + self.debit - self.credit

        super().save(*args, **kwargs)

    def __str__(self):

        if self.customer:
            name = self.customer.name
        else:
            name = self.supplier.name

        return f"{name} - {self.reference_no}"