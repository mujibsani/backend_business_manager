from django.conf import settings
from django.db import models
from django.db.models import Sum

from core.models import TimeStampedModel
from customers.models import Customer


# ==========================================================
# SALE
# ==========================================================

class Sale(TimeStampedModel):
    """
    Sales invoice.

    Business rules such as:
        - stock reduction
        - cashbook entry
        - customer ledger entry
        - invoice creation

    are handled by services.py.

    No signals are used.
    """

    class Status(models.TextChoices):
        PAID = "PAID", "Paid"
        PARTIAL = "PARTIAL", "Partial"
        UNPAID = "UNPAID", "Unpaid"

    invoice_no = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="sales",
    )

    sales_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="sales",
        null=True,
        blank=True,
    )

    date = models.DateField(
        db_index=True,
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    paid_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    due_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPAID,
        db_index=True,
    )

    def __str__(self):
        return self.invoice_no

    def update_totals(self):
        """
        Recalculate invoice totals from SaleItems.

        This method does NOT modify stock.

        Stock changes are handled by:
            sales.services.create_sale_invoice()
        """

        total = (
            self.items.aggregate(
                total=Sum("subtotal")
            )["total"]
            or 0
        )

        self.total_amount = total

        # Never allow a negative paid amount.
        if self.paid_amount < 0:
            self.paid_amount = 0

        # Prevent an invalid due amount.
        self.due_amount = (
            total - self.paid_amount
        )

        if self.due_amount <= 0:

            self.due_amount = 0
            self.status = self.Status.PAID

        elif self.paid_amount > 0:

            self.status = self.Status.PARTIAL

        else:

            self.status = self.Status.UNPAID

        self.save(
            update_fields=[
                "total_amount",
                "paid_amount",
                "due_amount",
                "status",
            ]
        )


# ==========================================================
# SALE ITEM
# ==========================================================

class SaleItem(TimeStampedModel):
    """
    Individual product line inside a sale invoice.

    subtotal is calculated automatically from:

        quantity × unit_price

    Stock is NOT changed here.

    Stock changes are handled explicitly by
    sales.services.create_sale_invoice().
    """

    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="sale_items",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        return (
            f"{self.sale.invoice_no} - "
            f"{self.product.name}"
        )

    def save(self, *args, **kwargs):
        """
        Calculate line subtotal before saving.
        """

        self.subtotal = (
            self.quantity * self.unit_price
        )

        super().save(*args, **kwargs)
