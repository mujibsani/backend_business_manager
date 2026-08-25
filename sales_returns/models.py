from django.conf import settings
from django.db import models
from django.db.models import Sum

from core.models import TimeStampedModel
from customers.models import Customer
from sales.models import Sale
from products.models import Product


class SalesReturn(TimeStampedModel):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    return_no = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    sale = models.ForeignKey(
        Sale,
        on_delete=models.PROTECT,
        related_name="returns",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="sales_returns",
    )

    date = models.DateField(
        db_index=True,
    )

    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    refund_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    reason = models.CharField(
        max_length=255,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED,
        db_index=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sales_returns",
    )

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Sales Return"
        verbose_name_plural = "Sales Returns"

    def __str__(self):
        return self.return_no

    def update_totals(self):
        total = (
            self.items.aggregate(
                total=Sum("subtotal")
            )["total"]
            or 0
        )

        self.total_amount = total

        self.save(
            update_fields=[
                "total_amount",
            ]
        )


class SalesReturnItem(TimeStampedModel):

    sales_return = models.ForeignKey(
        SalesReturn,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sales_return_items",
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

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):

        self.subtotal = (
            self.quantity * self.unit_price
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.sales_return.return_no} - "
            f"{self.product.name}"
        )