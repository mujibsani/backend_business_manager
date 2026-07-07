from django.db import models
from core.models import TimeStampedModel


class Supplier(TimeStampedModel):

    BALANCE_TYPE = (
        ("PAYABLE", "Payable"),
        ("ADVANCE", "Advance"),
    )

    name = models.CharField(max_length=200)

    phone = models.CharField(
        max_length=20,
        unique=True,
    )

    email = models.EmailField(
        blank=True,
    )

    division = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    thana = models.CharField(max_length=100)

    area = models.CharField(
        max_length=255,
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    opening_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    opening_balance_type = models.CharField(
        max_length=20,
        choices=BALANCE_TYPE,
        default="PAYABLE",
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name