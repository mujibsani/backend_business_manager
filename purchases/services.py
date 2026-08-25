from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Purchase, PurchaseItem

from products.models import Product
from products.services import stock_in

from cashbook.services import cash_out
from ledger.services import create_supplier_purchase_entry


# ==========================================================
# CREATE PURCHASE INVOICE
# ==========================================================

@transaction.atomic
def create_purchase_invoice(
    supplier,
    invoice_no,
    items,
    paid_amount=0,
    date=None,
):
    """
    Create a complete purchase invoice.

    Responsibilities:
        - Create purchase
        - Validate products
        - Validate quantities
        - Validate prices
        - Create purchase items
        - Increase stock
        - Calculate purchase totals
        - Create supplier ledger entry
        - Record actual cash payment

    items example:

    [
        {
            "product_id": 1,
            "quantity": 5,
            "unit_price": 100,
        }
    ]
    """

    # ------------------------------------------------------
    # BASIC VALIDATION
    # ------------------------------------------------------

    if supplier is None:
        raise ValidationError(
            "Supplier is required."
        )

    if not invoice_no:
        raise ValidationError(
            "Invoice number is required."
        )

    if not items:
        raise ValidationError(
            "At least one purchase item is required."
        )

    # ------------------------------------------------------
    # DECIMAL CONVERSION
    # ------------------------------------------------------

    try:
        paid_amount = Decimal(str(paid_amount))
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError(
            "Invalid paid amount."
        )

    if paid_amount < 0:
        raise ValidationError(
            "Paid amount cannot be negative."
        )

    # ------------------------------------------------------
    # CREATE PURCHASE
    # ------------------------------------------------------

    purchase = Purchase.objects.create(
        supplier=supplier,
        invoice_no=invoice_no,
        date=date,
        paid_amount=paid_amount,
    )

    # ------------------------------------------------------
    # CREATE PURCHASE ITEMS
    # ------------------------------------------------------

    for item in items:

        # --------------------------------------------------
        # PRODUCT ID
        # --------------------------------------------------

        product_id = item.get("product_id")

        if not product_id:
            raise ValidationError(
                "Product ID is required."
            )

        try:
            product = (
                Product.objects
                .select_for_update()
                .get(id=product_id)
            )

        except Product.DoesNotExist:
            raise ValidationError(
                f"Product ID {product_id} does not exist."
            )

        # --------------------------------------------------
        # QUANTITY
        # --------------------------------------------------

        try:
            quantity = Decimal(
                str(item.get("quantity"))
            )
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(
                f"Invalid quantity for {product.name}."
            )

        if quantity <= 0:
            raise ValidationError(
                f"Quantity must be greater than zero "
                f"for {product.name}."
            )

        # --------------------------------------------------
        # UNIT PRICE
        # --------------------------------------------------

        try:
            unit_price = Decimal(
                str(item.get("unit_price"))
            )
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(
                f"Invalid unit price for {product.name}."
            )

        if unit_price < 0:
            raise ValidationError(
                f"Unit price cannot be negative "
                f"for {product.name}."
            )

        # --------------------------------------------------
        # CREATE ITEM
        # --------------------------------------------------

        PurchaseItem.objects.create(
            purchase=purchase,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
        )

        # --------------------------------------------------
        # STOCK IN
        # --------------------------------------------------

        stock_in(
            product=product,
            quantity=quantity,
            reference=purchase.invoice_no,
        )

    # ------------------------------------------------------
    # CALCULATE TOTALS
    # ------------------------------------------------------

    purchase.update_totals()

    # ------------------------------------------------------
    # VALIDATE PAYMENT AGAINST TOTAL
    # ------------------------------------------------------

    if purchase.paid_amount > purchase.total_amount:
        raise ValidationError(
            "Paid amount cannot be greater than "
            "purchase total."
        )

    # ------------------------------------------------------
    # ACCOUNTING
    # ------------------------------------------------------

    process_purchase_accounting(
        purchase
    )

    return purchase


# ==========================================================
# PURCHASE ACCOUNTING
# ==========================================================

def process_purchase_accounting(purchase):
    """
    Create accounting transactions for a purchase.

    Full purchase amount:
        Supplier ledger liability

    Actual paid amount:
        Cashbook OUT
    """

    # ------------------------------------------------------
    # SUPPLIER LEDGER
    # ------------------------------------------------------

    create_supplier_purchase_entry(
        supplier=purchase.supplier,
        purchase=purchase,
    )

    # ------------------------------------------------------
    # CASHBOOK
    # ------------------------------------------------------
    # Only actual money paid is recorded as cash-out.
    # Unpaid/due amount remains as supplier liability.

    if purchase.paid_amount > 0:

        cash_out(
            amount=purchase.paid_amount,
            source_type="PURCHASE",
            date=purchase.date,
            reference=purchase.invoice_no,
            description=(
                f"Purchase Invoice "
                f"{purchase.invoice_no}"
            ),
        )