from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Sale, SaleItem
from products.models import Product, StockLog

@transaction.atomic
def create_sale_invoice(customer, invoice_no, items, paid_amount=0, date=None):
    """
    items format:
    [
        {"product_id": 1, "quantity": 2, "unit_price": 100},
        ...
    ]
    """

    sale = Sale.objects.create(
        customer=customer,
        invoice_no=invoice_no,
        date=date,
        total_amount=0,
        paid_amount=paid_amount,
        due_amount=0,
        status="UNPAID"
    )

    total = 0

    for item in items:
        product = Product.objects.select_for_update().get(id=item["product_id"])

        quantity = item["quantity"]

        # 🚨 STOCK VALIDATION
        if product.stock < quantity:
            raise ValidationError(f"Not enough stock for {product.name}")

        subtotal = quantity * item["unit_price"]
        total += subtotal

        # create item
        SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=item["unit_price"],
            subtotal=subtotal
        )

        # reduce stock
        product.stock -= quantity
        product.save()

        # stock log
        StockLog.objects.create(
            product=product,
            quantity=quantity,
            type="OUT",
            reference=f"SALE-{invoice_no}"
        )

    # finalize invoice
    sale.total_amount = total
    sale.due_amount = total - paid_amount

    if sale.due_amount <= 0:
        sale.status = "PAID"
        sale.due_amount = 0
    elif paid_amount > 0:
        sale.status = "PARTIAL"
    else:
        sale.status = "UNPAID"

    sale.save()

    return sale

from cashbook.services import create_cashbook_entry
from ledger.services import add_ledger_entry


def process_sale_accounting(sale, customer):

    # CASHBOOK ENTRY (IN)
    create_cashbook_entry(
        entry_type="IN",
        source_type="SALE",
        amount=sale.total_amount,
        reference=sale.invoice_no,
        description="Sale payment"
    )

    # LEDGER ENTRY (CUSTOMER DEBIT)
    add_ledger_entry(
        party_type="CUSTOMER",
        party_name=customer.name,
        debit=sale.total_amount,
        credit=0,
        description=f"Invoice {sale.invoice_no}"
    )