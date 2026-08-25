from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction

from cashbook.services import cash_in
from ledger.services import create_customer_sale_entry
from products.models import Product
from products.services import stock_out

from .models import Sale, SaleItem


@transaction.atomic
def create_sale_invoice(
    *,
    customer,
    invoice_no,
    items,
    paid_amount=Decimal("0.00"),
    date,
    sales_person=None,
):
    """
    Create a complete sale invoice.

    Handles:

    - Sale creation
    - Sale items
    - Stock reduction
    - Stock logs
    - Invoice totals
    - Customer ledger
    - Cashbook
    """

    # ------------------------------------------------------
    # PAID AMOUNT
    # ------------------------------------------------------

    try:
        paid_amount = Decimal(str(paid_amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(
            "Invalid paid amount."
        )

    if paid_amount < Decimal("0.00"):

        raise ValidationError(
            "Paid amount cannot be negative."
        )

    # ------------------------------------------------------
    # ITEMS
    # ------------------------------------------------------

    if not items:

        raise ValidationError(
            "At least one sale item is required."
        )

    # ------------------------------------------------------
    # DUPLICATE INVOICE
    # ------------------------------------------------------

    if Sale.objects.filter(
        invoice_no=invoice_no
    ).exists():

        raise ValidationError(
            "Invoice number already exists."
        )

    # ------------------------------------------------------
    # CREATE SALE
    # ------------------------------------------------------

    sale = Sale.objects.create(
        customer=customer,
        invoice_no=invoice_no,
        sales_person=sales_person,
        date=date,
        paid_amount=paid_amount,
    )

    total_amount = Decimal("0.00")

    # ------------------------------------------------------
    # CREATE ITEMS
    # ------------------------------------------------------

    for item in items:

        product_id = item.get(
            "product_id"
        )

        if not product_id:

            raise ValidationError(
                "product_id is required."
            )

        try:

            quantity = Decimal(
                str(item.get("quantity"))
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):

            raise ValidationError(
                "Invalid quantity."
            )

        try:

            unit_price = Decimal(
                str(item.get("unit_price"))
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):

            raise ValidationError(
                "Invalid unit price."
            )

        # --------------------------------------------------
        # QUANTITY
        # --------------------------------------------------

        if quantity <= Decimal("0.00"):

            raise ValidationError(
                "Quantity must be greater than zero."
            )

        # --------------------------------------------------
        # UNIT PRICE
        # --------------------------------------------------

        if unit_price < Decimal("0.00"):

            raise ValidationError(
                "Unit price cannot be negative."
            )

        # --------------------------------------------------
        # PRODUCT
        # --------------------------------------------------

        try:

            product = (
                Product.objects
                .select_for_update()
                .get(pk=product_id)
            )

        except Product.DoesNotExist:

            raise ValidationError(
                f"Product ID {product_id} "
                "does not exist."
            )

        # --------------------------------------------------
        # STOCK
        # --------------------------------------------------

        if product.stock < quantity:

            raise ValidationError(
                f"Not enough stock for "
                f"{product.name}. "
                f"Available stock: "
                f"{product.stock}"
            )

        # --------------------------------------------------
        # SUBTOTAL
        # --------------------------------------------------

        subtotal = quantity * unit_price

        # --------------------------------------------------
        # SALE ITEM
        # --------------------------------------------------

        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
        )

        # --------------------------------------------------
        # STOCK OUT
        # --------------------------------------------------

        stock_out(
            product=product,
            quantity=quantity,
            reference=f"SALE-{invoice_no}",
        )

        total_amount += subtotal

    # ------------------------------------------------------
    # PAID CANNOT EXCEED TOTAL
    # ------------------------------------------------------

    if paid_amount > total_amount:

        raise ValidationError(
            "Paid amount cannot be greater "
            "than invoice total."
        )

    # ------------------------------------------------------
    # UPDATE TOTALS
    # ------------------------------------------------------

    sale.update_totals()

    # ------------------------------------------------------
    # ACCOUNTING
    # ------------------------------------------------------

    process_sale_accounting(sale)

    return sale


def process_sale_accounting(sale):
    """
    Create accounting entries for a sale.

    Customer ledger:
        Invoice total becomes receivable.

    Cashbook:
        Only actual received cash is recorded.
    """

    create_customer_sale_entry(
        customer=sale.customer,
        sale=sale,
    )

    if sale.paid_amount > Decimal("0.00"):

        cash_in(
            amount=sale.paid_amount,
            source_type="SALE",
            date=sale.date,
            reference=sale.invoice_no,
            description=(
                f"Sale Invoice "
                f"{sale.invoice_no}"
            ),
        )