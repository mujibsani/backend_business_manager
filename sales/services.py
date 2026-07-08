from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Sale, SaleItem

from products.models import Product
from products.services import stock_out

from cashbook.services import cash_in
from ledger.services import create_customer_sale_entry


@transaction.atomic
def create_sale_invoice(
    customer,
    invoice_no,
    items,
    paid_amount=0,
    date=None,
    sales_person=None,
):
    """
    Create a sale invoice.

    items example:
    [
        {
            "product_id": 1,
            "quantity": 2,
            "unit_price": 100,
        }
    ]
    """

    sale = Sale.objects.create(
        customer=customer,
        invoice_no=invoice_no,
        sales_person=sales_person,
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

        if product.stock < quantity:
            raise ValidationError(
                f"Not enough stock for {product.name}"
            )

        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=item["unit_price"],
        )

        # Reduce stock
        stock_out(
            product=product,
            quantity=quantity,
            reference=invoice_no,
        )

    # Calculate invoice totals
    sale.update_totals()

    # Accounting
    process_sale_accounting(sale)

    return sale


def process_sale_accounting(sale):
    """
    Create accounting entries for a sale invoice.
    """

    # Customer Ledger (Customer Receivable)
    create_customer_sale_entry(
        customer=sale.customer,
        sale=sale,
    )

    # Cashbook
    # Only record cash if money was actually received.
    if sale.paid_amount > 0:
        cash_in(
            amount=sale.paid_amount,
            source_type="SALE",
            date=sale.date,
            reference=sale.invoice_no,
            description=f"Sale Invoice {sale.invoice_no}",
        )