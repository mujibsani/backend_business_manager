from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Product, StockLog


@transaction.atomic
def stock_in(
    product,
    quantity,
    reference,
):
    """
    Increase product stock.
    Used by:
        Purchase
        Stock Adjustment
        Sales Return
    """

    quantity = Decimal(str(quantity))

    product.stock += quantity
    product.save(update_fields=["stock"])

    StockLog.objects.create(
        product=product,
        quantity=quantity,
        type="IN",
        reference=reference,
    )


@transaction.atomic
def stock_out(
    product,
    quantity,
    reference,
):
    """
    Reduce product stock.
    Used by:
        Sale
        Damage
        Purchase Return
    """

    quantity = Decimal(str(quantity))

    if product.stock < quantity:
        raise ValidationError(
            f"Not enough stock for {product.name}"
        )

    product.stock -= quantity
    product.save(update_fields=["stock"])

    StockLog.objects.create(
        product=product,
        quantity=quantity,
        type="OUT",
        reference=reference,
    )


def available_stock(product):

    return product.stock