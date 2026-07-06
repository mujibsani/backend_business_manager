from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

from core.models import TimeStampedModel
from customers.models import Customer
from suppliers.models import Supplier


class Payment(TimeStampedModel):

    PAYMENT_TYPE = (
        ("CUSTOMER", "Customer"),
        ("SUPPLIER", "Supplier"),
    )

    PAYMENT_METHOD = (
        ("CASH", "Cash"),
        ("BANK", "Bank Transfer"),
        ("BKASH", "bKash"),
        ("NAGAD", "Nagad"),
        ("CARD", "Card"),
        ("CHEQUE", "Cheque"),
    )

    STATUS_CHOICES = (
        ("COMPLETED", "Completed"),
        ("PENDING", "Pending"),
        ("CANCELLED", "Cancelled"),
    )

    payment_no = models.CharField(
        max_length=50,
        unique=True
    )

    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments"
    )

    sale = models.ForeignKey(
        "sales.Sale",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments"
    )

    purchase = models.ForeignKey(
        "purchases.Purchase",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        default="CASH"
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True
    )

    reference_no = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bank reference, cheque number, mobile transaction ID, etc."
    )

    payment_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="COMPLETED"
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="received_payments"
    )

    note = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["-payment_date", "-id"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def clean(self):

        if self.payment_type == "CUSTOMER":

            if not self.customer:
                raise ValidationError("Customer is required.")

            if self.supplier:
                raise ValidationError("Supplier must be empty for customer payment.")

            if self.sale and self.sale.customer != self.customer:
                raise ValidationError("Selected sale does not belong to this customer.")

        elif self.payment_type == "SUPPLIER":

            if not self.supplier:
                raise ValidationError("Supplier is required.")

            if self.customer:
                raise ValidationError("Customer must be empty for supplier payment.")

            if self.purchase and self.purchase.supplier != self.supplier:
                raise ValidationError("Selected purchase does not belong to this supplier.")

    def __str__(self):

        if self.payment_type == "CUSTOMER":
            party = self.customer.name if self.customer else "Customer Advance"
        else:
            party = self.supplier.name if self.supplier else "Supplier Advance"

        return f"{self.payment_no} | {party} | {self.amount}"