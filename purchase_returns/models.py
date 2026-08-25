from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

from core.models import TimeStampedModel
from purchases.models import Purchase
from products.models import Product
from suppliers.models import Supplier


class PurchaseReturn(TimeStampedModel):

    STATUS_CHOICES = (
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    return_no = models.CharField(
        max_length=50,
        unique=True,
    )

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.PROTECT,
        related_name="returns",
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchase_returns",
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

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="COMPLETED",
    )

    reason = models.CharField(
        max_length=255,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_purchase_returns",
    )

    class Meta:
        ordering = ["-date", "-id"]
        verbose_name = "Purchase Return"
        verbose_name_plural = "Purchase Returns"

    def clean(self):

        if self.purchase_id and self.supplier_id:

            if self.supplier_id != self.purchase.supplier_id:
                raise ValidationError(
                    "Supplier must match the original purchase."
                )

        if self.total_amount < 0:
            raise ValidationError(
                "Return amount cannot be negative."
            )

        if self.refund_amount < 0:
            raise ValidationError(
                "Refund amount cannot be negative."
            )

        if self.refund_amount > self.total_amount:
            raise ValidationError(
                "Refund amount cannot exceed return amount."
            )

    def __str__(self):
        return f"{self.return_no} | {self.supplier.name}"


class PurchaseReturnItem(TimeStampedModel):

    purchase_return = models.ForeignKey(
        PurchaseReturn,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchase_return_items",
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

    def clean(self):

        if self.quantity <= 0:
            raise ValidationError(
                "Return quantity must be greater than zero."
            )

        if self.unit_price < 0:
            raise ValidationError(
                "Unit price cannot be negative."
            )

        if self.purchase_return_id and self.product_id:

            purchase = self.purchase_return.purchase

            exists = purchase.items.filter(
                product=self.product
            ).exists()

            if not exists:
                raise ValidationError(
                    "Product was not part of the original purchase."
                )

    def save(self, *args, **kwargs):

        self.subtotal = (
            self.quantity * self.unit_price
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.purchase_return.return_no} | "
            f"{self.product.name} | "
            f"{self.quantity}"
        )