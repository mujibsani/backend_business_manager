from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Purchase, PurchaseItem
from products.models import Product, StockLog
from .services import process_purchase_accounting


@transaction.atomic
def create_purchase_invoice(supplier, invoice_no, items, paid_amount=0, date=None):
    """
    items format:
    [
        {"product_id": 1, "quantity": 5, "unit_price": 100},
        ...
    ]
    """

    purchase = Purchase.objects.create(
        supplier=supplier,
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

        subtotal = quantity * item["unit_price"]
        total += subtotal

        # create purchase item
        PurchaseItem.objects.create(
            purchase=purchase,
            product=product,
            quantity=quantity,
            unit_price=item["unit_price"],
            subtotal=subtotal
        )

        # 🚀 INCREASE STOCK (purchase increases inventory)
        product.stock += quantity
        product.save()

        # stock log
        StockLog.objects.create(
            product=product,
            quantity=quantity,
            type="IN",
            reference=f"PURCHASE-{invoice_no}"
        )

    # finalize invoice
    purchase.total_amount = total
    purchase.due_amount = total - paid_amount

    if purchase.due_amount <= 0:
        purchase.status = "PAID"
        purchase.due_amount = 0
    elif paid_amount > 0:
        purchase.status = "PARTIAL"
    else:
        purchase.status = "UNPAID"

    purchase.save()

    

    return purchase


from cashbook.services import create_cashbook_entry
from ledger.services import add_ledger_entry


def process_purchase_accounting(purchase, supplier):

    # CASHBOOK ENTRY (OUT)
    create_cashbook_entry(
        entry_type="OUT",
        source_type="PURCHASE",
        amount=purchase.total_amount,
        reference=purchase.invoice_no,
        description="Purchase payment"
    )

    # LEDGER ENTRY (SUPPLIER CREDIT)
    add_ledger_entry(
        party_type="SUPPLIER",
        party_name=supplier.name,
        debit=0,
        credit=purchase.total_amount,
        description=f"Purchase {purchase.invoice_no}"
    )