from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from customers.models import Customer
from sales.models import Sale
from products.models import Product


class SalesReturn(TimeStampedModel):

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    return_no = models.CharField(
        max_length=50,
        unique=True,
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

    date = models.DateField()

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
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sales_returns",
    )

    def __str__(self):
        return self.return_no

    def update_totals(self):

        total = sum(item.subtotal for item in self.items.all())

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

    def save(self, *args, **kwargs):

        self.subtotal = self.quantity * self.unit_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sales_return.return_no} - {self.product.name}"
