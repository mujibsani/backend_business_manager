from django.db import models
from django.db.models import Sum

from core.models import TimeStampedModel
from suppliers.models import Supplier


class Purchase(TimeStampedModel):

    STATUS_CHOICES = (
        ("PAID", "Paid"),
        ("PARTIAL", "Partial"),
        ("UNPAID", "Unpaid"),
    )

    invoice_no = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)

    date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    paid_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    due_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="UNPAID"
    )

    def __str__(self):
        return self.invoice_no

    def update_totals(self):

        total = (
            self.items.aggregate(total=Sum("subtotal"))["total"]
            or 0
        )

        self.total_amount = total
        self.due_amount = total - self.paid_amount

        if self.due_amount <= 0:
            self.status = "PAID"
            self.due_amount = 0
        elif self.paid_amount > 0:
            self.status = "PARTIAL"
        else:
            self.status = "UNPAID"

        self.save(update_fields=[
            "total_amount",
            "due_amount",
            "status",
        ])


class PurchaseItem(TimeStampedModel):

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)