from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import SalesReturn, SalesReturnItem

from products.models import Product
from products.services import stock_in

from cashbook.services import cash_out
from ledger.services import create_customer_sales_return_entry


# ==========================================================
# RETURN NUMBER GENERATOR
# ==========================================================

def generate_return_no():
    """
    Generates sequential return number:
    SR-000001
    SR-000002
    """

    last = SalesReturn.objects.order_by("-id").first()

    if not last:
        return "SR-000001"

    try:
        number = int(last.return_no.split("-")[1])
    except Exception:
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
    """
    Recalculate the original sale after a return.

    Example:

    Original
        Total = 10000
        Paid  = 6000
        Due   = 4000

    Return = 2000
    Refund = 1000

    New
        Total = 8000
        Paid  = 5000
        Due   = 3000
    """

    return_amount = Decimal(str(return_amount))
    refund_amount = Decimal(str(refund_amount))

    # Reduce invoice amount
    sale.total_amount -= return_amount

    if sale.total_amount < Decimal("0.00"):
        sale.total_amount = Decimal("0.00")

    # Reduce paid amount if refund issued
    if refund_amount > Decimal("0.00"):

        sale.paid_amount -= refund_amount

        if sale.paid_amount < Decimal("0.00"):
            sale.paid_amount = Decimal("0.00")

    # Recalculate due
    sale.due_amount = sale.total_amount - sale.paid_amount

    if sale.due_amount <= Decimal("0.00"):
        sale.status = "PAID"
        sale.due_amount = Decimal("0.00")

    elif sale.paid_amount > Decimal("0.00"):
        sale.status = "PARTIAL"

    else:
        sale.status = "UNPAID"

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
):
    """
    Creates a complete sales return.

    Responsibilities

    ✔ Create Sales Return
    ✔ Create Return Items
    ✔ Increase Stock
    ✔ Update Original Sale
    ✔ Customer Ledger
    ✔ Cashbook (Refund)
    """

    refund_amount = Decimal(str(refund_amount))

    sales_return = SalesReturn.objects.create(
        return_no=generate_return_no(),
        sale=sale,
        customer=sale.customer,
        date=sale.date,
        refund_amount=refund_amount,
        reason=reason,
        status="COMPLETED",
        created_by=created_by,
    )

    total_return = Decimal("0.00")

    for item in items:

        product = Product.objects.select_for_update().get(
            id=item["product_id"]
        )

        quantity = Decimal(str(item["quantity"]))
        unit_price = Decimal(str(item["unit_price"]))

        if quantity <= 0:
            raise ValidationError(
                f"Invalid quantity for '{product.name}'."
            )

        # Prevent returning more than sold
        sold_qty = (
            sale.items.filter(product=product)
            .aggregate(total_quantity=Sum("quantity"))
            .get("total_quantity")
            or Decimal("0.00")
        )

        returned_qty = (
            SalesReturnItem.objects.filter(
                sales_return__sale=sale,
                product=product,
            )
            .aggregate(total_quantity=Sum("quantity"))
            .get("total_quantity")
            or Decimal("0.00")
        )

        available_return_qty = sold_qty - returned_qty

        if quantity > available_return_qty:
            raise ValidationError(
                f"You can return only {available_return_qty} "
                f"{product.name}. Already returned: {returned_qty}."
            )

        subtotal = quantity * unit_price

        SalesReturnItem.objects.create(
            sales_return=sales_return,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
        )

        total_return += subtotal

        # Increase stock
        stock_in(
            product=product,
            quantity=quantity,
            reference=sales_return.return_no,
        )

    sales_return.total_amount = total_return

    sales_return.save(
        update_fields=[
            "total_amount",
        ]
    )

    # Update original invoice
    _update_sale_after_return(
        sale=sale,
        return_amount=total_return,
        refund_amount=refund_amount,
    )

    # Customer Ledger
    create_customer_sales_return_entry(
        customer=sale.customer,
        sales_return=sales_return,
    )

    # Refund Cash (if applicable)
    if refund_amount > Decimal("0.00"):

        cash_out(
            amount=refund_amount,
            source_type="SALE_RETURN",
            date=sales_return.date,
            reference=sales_return.return_no,
            description=f"Refund against {sales_return.return_no}",
        )

    return sales_return