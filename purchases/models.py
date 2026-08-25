from django.db import models
from django.db.models import Sum

from core.models import TimeStampedModel
from suppliers.models import Supplier


# ==========================================================
# PURCHASE
# ==========================================================

class Purchase(TimeStampedModel):
    """
    Purchase invoice.

    Business operations such as:
        - stock increase
        - supplier ledger
        - cashbook
        - invoice creation

    are handled by purchases.services.

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

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchases",
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
        Recalculate purchase totals from PurchaseItems.

        This method does NOT change stock.

        Stock changes are handled explicitly by:
            purchases.services.create_purchase_invoice()
        """

        total = (
            self.items.aggregate(
                total=Sum("subtotal")
            )["total"]
            or 0
        )

        self.total_amount = total

        # Never allow negative paid amount.
        if self.paid_amount < 0:
            self.paid_amount = 0

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
# PURCHASE ITEM
# ==========================================================

class PurchaseItem(TimeStampedModel):
    """
    Individual product line inside a purchase invoice.

    subtotal = quantity × unit_price

    Stock is NOT changed here.

    Stock changes are handled by:
        purchases.services.create_purchase_invoice()
    """

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="purchase_items",
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
            f"{self.purchase.invoice_no} - "
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
