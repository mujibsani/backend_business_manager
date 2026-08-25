from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from .models import (
    SalesReturn,
    SalesReturnItem,
)

from products.models import Product
from products.services import stock_in

from sales.models import Sale

from cashbook.services import cash_out

from ledger.services import (
    create_customer_sales_return_entry,
)


# ==========================================================
# DECIMAL HELPER
# ==========================================================

def _to_decimal(value):

    try:
        return Decimal(str(value))

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):

        raise ValidationError(
            f"Invalid decimal value: {value}"
        )


# ==========================================================
# RETURN NUMBER GENERATOR
# ==========================================================

def generate_return_no():

    last = (
        SalesReturn.objects
        .order_by("-id")
        .first()
    )

    if not last:
        return "SR-000001"

    try:

        number = int(
            last.return_no.split("-")[1]
        )

    except (
        ValueError,
        IndexError,
    ):

        number = last.id

    return f"SR-{number + 1:06d}"


# ==========================================================
# UPDATE ORIGINAL SALE
# ==========================================================

def _update_sale_after_return(
    sale,
    return_amount,
    refund_amount=Decimal("0.00"),
):

    return_amount = _to_decimal(
        return_amount
    )

    refund_amount = _to_decimal(
        refund_amount
    )

    if return_amount <= Decimal("0.00"):
        raise ValidationError(
            "Return amount must be greater than zero."
        )

    if refund_amount < Decimal("0.00"):
        raise ValidationError(
            "Refund amount cannot be negative."
        )

    if refund_amount > return_amount:
        raise ValidationError(
            "Refund amount cannot exceed "
            "return amount."
        )

    if refund_amount > sale.paid_amount:
        raise ValidationError(
            "Refund amount cannot exceed "
            "the amount already paid."
        )

    # ------------------------------------------------------
    # REDUCE SALE TOTAL
    # ------------------------------------------------------

    sale.total_amount -= return_amount

    if sale.total_amount < Decimal("0.00"):

        sale.total_amount = Decimal("0.00")

    # ------------------------------------------------------
    # REDUCE PAID AMOUNT BY REFUND
    # ------------------------------------------------------

    if refund_amount > Decimal("0.00"):

        sale.paid_amount -= refund_amount

        if sale.paid_amount < Decimal("0.00"):

            sale.paid_amount = Decimal("0.00")

    # ------------------------------------------------------
    # RECALCULATE DUE
    # ------------------------------------------------------

    sale.due_amount = (
        sale.total_amount
        - sale.paid_amount
    )

    if sale.due_amount < Decimal("0.00"):

        sale.due_amount = Decimal("0.00")

    # ------------------------------------------------------
    # STATUS
    # ------------------------------------------------------

    if sale.due_amount == Decimal("0.00"):

        sale.status = Sale.Status.PAID

    elif sale.paid_amount > Decimal("0.00"):

        sale.status = Sale.Status.PARTIAL

    else:

        sale.status = Sale.Status.UNPAID

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    sale.save(
        update_fields=[
            "total_amount",
            "paid_amount",
            "due_amount",
            "status",
        ]
    )


# ==========================================================
# CREATE SALES RETURN
# ==========================================================

@transaction.atomic
def create_sales_return(
    sale,
    items,
    refund_amount=Decimal("0.00"),
    reason="",
    created_by=None,
    date=None,
):

    # ======================================================
    # BASIC VALIDATION
    # ======================================================

    if not sale:
        raise ValidationError(
            "Sale is required."
        )

    if not items:
        raise ValidationError(
            "Return items are required."
        )

    # ======================================================
    # LOCK SALE
    # ======================================================

    sale = (
        Sale.objects
        .select_for_update()
        .select_related("customer")
        .get(pk=sale.pk)
    )

    # ======================================================
    # REFUND
    # ======================================================

    refund_amount = _to_decimal(
        refund_amount
    )

    if refund_amount < Decimal("0.00"):

        raise ValidationError(
            "Refund amount cannot be negative."
        )

    if refund_amount > sale.paid_amount:

        raise ValidationError(
            "Refund amount cannot exceed "
            "the amount already paid."
        )

    # ======================================================
    # DATE
    # ======================================================

    return_date = (
        date
        if date is not None
        else sale.date
    )

    # ======================================================
    # CREATE HEADER
    # ======================================================

    sales_return = SalesReturn.objects.create(
        return_no=generate_return_no(),
        sale=sale,
        customer=sale.customer,
        date=return_date,
        total_amount=Decimal("0.00"),
        refund_amount=refund_amount,
        reason=reason,
        status=SalesReturn.Status.COMPLETED,
        created_by=created_by,
    )

    total_return = Decimal("0.00")

    processed_products = set()

    # ======================================================
    # PROCESS ITEMS
    # ======================================================

    for item in items:

        product_id = item.get(
            "product_id"
        )

        # --------------------------------------------------
        # Support internal service calls using Product
        # --------------------------------------------------

        product = item.get("product")

        if product is not None:

            product_id = product.pk

        if not product_id:

            raise ValidationError(
                "Product is required."
            )

        # --------------------------------------------------
        # Prevent duplicate product lines
        # --------------------------------------------------

        if product_id in processed_products:

            raise ValidationError(
                f"Product {product_id} appears more "
                f"than once in the return."
            )

        processed_products.add(
            product_id
        )

        # --------------------------------------------------
        # LOCK PRODUCT
        # --------------------------------------------------

        try:

            product = (
                Product.objects
                .select_for_update()
                .get(pk=product_id)
            )

        except Product.DoesNotExist:

            raise ValidationError(
                f"Product {product_id} not found."
            )

        # --------------------------------------------------
        # QUANTITY
        # --------------------------------------------------

        quantity = _to_decimal(
            item.get("quantity", 0)
        )

        if quantity <= Decimal("0.00"):

            raise ValidationError(
                f"Return quantity for "
                f"{product.name} must be greater than zero."
            )

        # ==================================================
        # ORIGINAL SALE ITEM
        # ==================================================

        sale_item = (
            sale.items
            .filter(product=product)
            .first()
        )

        if not sale_item:

            raise ValidationError(
                f"{product.name} was not included "
                f"in sale {sale.invoice_no}."
            )

        # ==================================================
        # ORIGINAL UNIT PRICE
        # ==================================================

        unit_price = _to_decimal(
            sale_item.unit_price
        )

        # ==================================================
        # SOLD QUANTITY
        # ==================================================

        sold_quantity = (
            sale.items
            .filter(product=product)
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or Decimal("0.00")
        )

        # ==================================================
        # PREVIOUSLY RETURNED
        # ==================================================

        returned_quantity = (
            SalesReturnItem.objects
            .filter(
                sales_return__sale=sale,
                sales_return__status=(
                    SalesReturn.Status.COMPLETED
                ),
                product=product,
            )
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or Decimal("0.00")
        )

        # ==================================================
        # AVAILABLE RETURN
        # ==================================================

        available_quantity = (
            sold_quantity
            - returned_quantity
        )

        if quantity > available_quantity:

            raise ValidationError(
                f"Cannot return {quantity} "
                f"{product.name}. "
                f"Only {available_quantity} "
                f"is available for return."
            )

        # ==================================================
        # SUBTOTAL
        # ==================================================

        subtotal = (
            quantity * unit_price
        )

        total_return += subtotal

        # ==================================================
        # CREATE ITEM
        # ==================================================

        SalesReturnItem.objects.create(
            sales_return=sales_return,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
        )

        # ==================================================
        # STOCK IN
        # ==================================================

        stock_in(
            product=product,
            quantity=quantity,
            reference=sales_return.return_no,
        )

    # ======================================================
    # RETURN TOTAL
    # ======================================================

    if total_return <= Decimal("0.00"):

        raise ValidationError(
            "Return amount must be greater than zero."
        )

    # ======================================================
    # REFUND VALIDATION
    # ======================================================

    if refund_amount > total_return:

        raise ValidationError(
            "Refund amount cannot exceed "
            "the total return amount."
        )

    if refund_amount > sale.paid_amount:

        raise ValidationError(
            "Refund amount cannot exceed "
            "the amount already paid."
        )

    # ======================================================
    # UPDATE RETURN HEADER
    # ======================================================

    sales_return.total_amount = total_return

    sales_return.save(
        update_fields=[
            "total_amount",
        ]
    )

    # ======================================================
    # UPDATE ORIGINAL SALE
    # ======================================================

    _update_sale_after_return(
        sale=sale,
        return_amount=total_return,
        refund_amount=refund_amount,
    )

    # ======================================================
    # CUSTOMER LEDGER
    # ======================================================

    create_customer_sales_return_entry(
        customer=sale.customer,
        sales_return=sales_return,
    )

    # ======================================================
    # CASHBOOK REFUND
    # ======================================================

    if refund_amount > Decimal("0.00"):

        cash_out(
            amount=refund_amount,
            source_type="SALE_RETURN",
            date=sales_return.date,
            reference=sales_return.return_no,
            description=(
                f"Refund against "
                f"{sales_return.return_no}"
            ),
        )

    return sales_return