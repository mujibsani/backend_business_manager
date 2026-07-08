from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Purchase, PurchaseItem

from products.models import Product
from products.services import stock_in

from cashbook.services import cash_out
from ledger.services import create_supplier_purchase_entry


@transaction.atomic
def create_purchase_invoice(
    supplier,
    invoice_no,
    items,
    paid_amount=0,
    date=None,
):
    """
    Create a purchase invoice.

    items example:
    [
        {
            "product_id": 1,
            "quantity": 5,
            "unit_price": 100,
        }
    ]
    """

    purchase = Purchase.objects.create(
        supplier=supplier,
        invoice_no=invoice_no,
        date=date,
        paid_amount=paid_amount,
    )

    for item in items:
        try:
            product = Product.objects.select_for_update().get(
                id=item["product_id"]
            )
        except Product.DoesNotExist:
            raise ValidationError(
                f"Product ID {item['product_id']} does not exist."
            )

        quantity = item["quantity"]

        if quantity <= 0:
            raise ValidationError(
                f"Invalid quantity for {product.name}"
            )

        PurchaseItem.objects.create(
            purchase=purchase,
            product=product,
            quantity=quantity,
            unit_price=item["unit_price"],
        )

        # Increase stock
        stock_in(
            product=product,
            quantity=quantity,
            reference=invoice_no,
        )

    # Calculate totals
    purchase.update_totals()

    # Accounting
    process_purchase_accounting(purchase)

    return purchase


def process_purchase_accounting(purchase):
    """
    Create accounting transactions for a purchase invoice.
    """

    cash_out(
        amount=purchase.total_amount,
        source_type="PURCHASE",
        date=purchase.date,
        reference=purchase.invoice_no,
        description=f"Purchase Invoice {purchase.invoice_no}",
    )

    create_supplier_purchase_entry(
        supplier=purchase.supplier,
        purchase=purchase,
    )