from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum

from .models import PurchaseReturn, PurchaseReturnItem

from products.models import Product
from products.services import stock_out

from ledger.services import (
    create_supplier_purchase_return_entry,
)

from cashbook.services import cash_in


# ==========================================================
# RETURN NUMBER GENERATOR
# ==========================================================

def generate_purchase_return_no():
    """
    Generate sequential purchase return numbers.

    Examples:
        PR-000001
        PR-000002
        PR-000003
    """

    last_return = (
        PurchaseReturn.objects
        .order_by("-id")
        .first()
    )

    if not last_return:
        return "PR-000001"

    try:
        last_number = int(
            last_return.return_no.split("-")[1]
        )
    except (ValueError, IndexError):
        last_number = last_return.id

    return f"PR-{last_number + 1:06d}"


# ==========================================================
# DECIMAL HELPER
# ==========================================================

def _to_decimal(value):
    """
    Safely convert a value to Decimal.
    """

    try:
        return Decimal(str(value))
    except (TypeError, ValueError):
        raise ValidationError(
            f"Invalid decimal value: {value}"
        )


# ==========================================================
# AMOUNT VALIDATION
# ==========================================================

def _validate_amount(amount):
    """
    Convert amount to Decimal and make sure
    it is not negative.
    """

    amount = _to_decimal(amount)

    if amount < Decimal("0.00"):
        raise ValidationError(
            "Amount cannot be negative."
        )

    return amount


# ==========================================================
# UPDATE ORIGINAL PURCHASE
# ==========================================================

def _update_purchase_after_return(
    purchase,
    return_amount,
    refund_amount=Decimal("0.00"),
):
    """
    Update the original purchase after a return.

    Example:

        Original Purchase
        -----------------
        Total = 10,000
        Paid  = 6,000
        Due   = 4,000

        Return = 2,000
        Refund = 1,000

        New Purchase
        -------------
        Total = 8,000
        Paid  = 5,000
        Due   = 3,000
    """

    return_amount = _to_decimal(return_amount)
    refund_amount = _to_decimal(refund_amount)

    # ------------------------------------------------------
    # Safety validation
    # ------------------------------------------------------

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
            "Refund amount cannot exceed return amount."
        )

    # Cash refund cannot exceed what was actually paid.
    if refund_amount > purchase.paid_amount:
        raise ValidationError(
            "Supplier refund cannot exceed "
            "the amount already paid for the purchase."
        )

    # ------------------------------------------------------
    # Reduce purchase total
    # ------------------------------------------------------

    purchase.total_amount -= return_amount

    if purchase.total_amount < Decimal("0.00"):
        purchase.total_amount = Decimal("0.00")

    # ------------------------------------------------------
    # Reduce paid amount by actual cash refund
    # ------------------------------------------------------

    if refund_amount > Decimal("0.00"):

        purchase.paid_amount -= refund_amount

        if purchase.paid_amount < Decimal("0.00"):
            purchase.paid_amount = Decimal("0.00")

    # ------------------------------------------------------
    # Recalculate due
    # ------------------------------------------------------

    purchase.due_amount = (
        purchase.total_amount
        - purchase.paid_amount
    )

    if purchase.due_amount < Decimal("0.00"):
        purchase.due_amount = Decimal("0.00")

    # ------------------------------------------------------
    # Update status
    # ------------------------------------------------------

    if purchase.due_amount == Decimal("0.00"):

        purchase.status = "PAID"

    elif purchase.paid_amount > Decimal("0.00"):

        purchase.status = "PARTIAL"

    else:

        purchase.status = "UNPAID"

    # ------------------------------------------------------
    # Save
    # ------------------------------------------------------

    purchase.save(
        update_fields=[
            "total_amount",
            "paid_amount",
            "due_amount",
            "status",
        ]
    )


# ==========================================================
# CREATE PURCHASE RETURN
# ==========================================================

@transaction.atomic
def create_purchase_return(
    purchase,
    supplier,
    items,
    refund_amount=Decimal("0.00"),
    reason="",
    created_by=None,
    date=None,
):
    """
    Create a completed purchase return.

    Responsibilities:

    1. Validate purchase
    2. Validate supplier
    3. Lock purchase
    4. Validate return items
    5. Prevent over-return
    6. Use original purchase price
    7. Create PurchaseReturn
    8. Create PurchaseReturnItems
    9. Reduce stock
    10. Update original Purchase
    11. Create supplier ledger entry
    12. Record supplier cash refund
    """

    # ======================================================
    # BASIC VALIDATION
    # ======================================================

    if not purchase:
        raise ValidationError(
            "Purchase is required."
        )

    if not supplier:
        raise ValidationError(
            "Supplier is required."
        )

    if not items:
        raise ValidationError(
            "Return items are required."
        )

    # ======================================================
    # VALIDATE SUPPLIER
    # ======================================================

    if purchase.supplier_id != supplier.id:
        raise ValidationError(
            "Supplier does not match the purchase supplier."
        )

    # ======================================================
    # VALIDATE REFUND
    # ======================================================

    refund_amount = _validate_amount(
        refund_amount
    )

    # ======================================================
    # LOCK PURCHASE
    # ======================================================

    purchase = (
        purchase.__class__
        .objects
        .select_for_update()
        .get(pk=purchase.pk)
    )

    # ======================================================
    # VALIDATE REFUND AGAINST PURCHASE
    # ======================================================

    if refund_amount > purchase.paid_amount:
        raise ValidationError(
            "Supplier refund cannot exceed "
            "the amount already paid for the purchase."
        )

    # ======================================================
    # RETURN DATE
    # ======================================================

    purchase_return_date = (
        date
        if date is not None
        else purchase.date
    )

    # ======================================================
    # CREATE RETURN HEADER
    # ======================================================

    purchase_return = PurchaseReturn.objects.create(
        return_no=generate_purchase_return_no(),
        purchase=purchase,
        supplier=supplier,
        date=purchase_return_date,
        total_amount=Decimal("0.00"),
        refund_amount=refund_amount,
        status="COMPLETED",
        reason=reason,
        created_by=created_by,
    )

    total_return = Decimal("0.00")

    # ======================================================
    # TRACK PRODUCTS IN THIS RETURN
    # ======================================================

    processed_products = set()

    # ======================================================
    # PROCESS RETURN ITEMS
    # ======================================================

    for item in items:

        # --------------------------------------------------
        # Accept either:
        #
        # {
        #     "product": product,
        #     "quantity": 2
        # }
        #
        # OR:
        #
        # {
        #     "product_id": product.id,
        #     "quantity": 2
        # }
        # --------------------------------------------------

        product = item.get("product")

        product_id = item.get("product_id")

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
                f"Product {product_id} appears more than "
                f"once in the return."
            )

        processed_products.add(product_id)

        # --------------------------------------------------
        # Lock product
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
        # Quantity
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
        # FIND ORIGINAL PURCHASE ITEM
        # ==================================================

        purchase_item = (
            purchase.items
            .filter(product=product)
            .first()
        )

        if not purchase_item:
            raise ValidationError(
                f"{product.name} was not included "
                f"in purchase {purchase.invoice_no}."
            )

        # ==================================================
        # USE ORIGINAL PURCHASE PRICE
        # ==================================================

        unit_price = _to_decimal(
            purchase_item.unit_price
        )

        # ==================================================
        # TOTAL PURCHASED QUANTITY
        # ==================================================

        purchased_quantity = (
            purchase.items
            .filter(product=product)
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or Decimal("0.00")
        )

        # ==================================================
        # PREVIOUSLY RETURNED QUANTITY
        # ==================================================

        previously_returned = (
            PurchaseReturnItem.objects
            .filter(
                purchase_return__purchase=purchase,
                product=product,
                purchase_return__status="COMPLETED",
            )
            .aggregate(
                total=Sum("quantity")
            )["total"]
            or Decimal("0.00")
        )

        # ==================================================
        # AVAILABLE RETURN QUANTITY
        # ==================================================

        available_quantity = (
            purchased_quantity
            - previously_returned
        )

        if quantity > available_quantity:
            raise ValidationError(
                f"Cannot return {quantity} "
                f"{product.name}. "
                f"Only {available_quantity} "
                f"is available for return."
            )

        # ==================================================
        # CHECK CURRENT STOCK
        # ==================================================

        if product.stock < quantity:
            raise ValidationError(
                f"Not enough stock to return "
                f"{quantity} {product.name}."
            )

        # ==================================================
        # SUBTOTAL
        # ==================================================

        subtotal = quantity * unit_price

        total_return += subtotal

        # ==================================================
        # CREATE RETURN ITEM
        # ==================================================

        PurchaseReturnItem.objects.create(
            purchase_return=purchase_return,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
        )

        # ==================================================
        # REDUCE STOCK
        # ==================================================

        stock_out(
            product=product,
            quantity=quantity,
            reference=purchase_return.return_no,
        )

    # ======================================================
    # VALIDATE RETURN TOTAL
    # ======================================================

    if total_return <= Decimal("0.00"):
        raise ValidationError(
            "Return amount must be greater than zero."
        )

    # ======================================================
    # VALIDATE REFUND AGAINST RETURN
    # ======================================================

    if refund_amount > total_return:
        raise ValidationError(
            "Supplier refund cannot exceed "
            "the total return amount."
        )

    if refund_amount > purchase.paid_amount:
        raise ValidationError(
            "Supplier refund cannot exceed "
            "the amount already paid for the purchase."
        )

    # ======================================================
    # UPDATE RETURN HEADER
    # ======================================================

    purchase_return.total_amount = total_return

    purchase_return.save(
        update_fields=[
            "total_amount",
        ]
    )

    # ======================================================
    # UPDATE ORIGINAL PURCHASE
    # ======================================================

    _update_purchase_after_return(
        purchase=purchase,
        return_amount=total_return,
        refund_amount=refund_amount,
    )

    # ======================================================
    # SUPPLIER LEDGER
    # ======================================================

    create_supplier_purchase_return_entry(
        supplier=supplier,
        purchase_return=purchase_return,
    )

    # ======================================================
    # CASHBOOK
    # ======================================================

    if refund_amount > Decimal("0.00"):

        cash_in(
            amount=refund_amount,
            source_type="PURCHASE_RETURN",
            date=purchase_return.date,
            reference=purchase_return.return_no,
            description=(
                f"Supplier refund for "
                f"{purchase_return.return_no}"
            ),
        )

    return purchase_return