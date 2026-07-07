from django.db import models
from core.models import TimeStampedModel

from locations.models import Division, District, Thana


class Customer(TimeStampedModel):

    BALANCE_TYPE = (
        ("RECEIVABLE", "Receivable"),
        ("PAYABLE", "Payable"),
    )
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)

    division = models.ForeignKey(
        Division,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    thana = models.ForeignKey(
        Thana,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    area = models.CharField(
        max_length=255,
        blank=True,
        help_text="Village / Road / House / Market"
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
        default="RECEIVABLE",
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name



    