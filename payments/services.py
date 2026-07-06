from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from .models import Payment

from sales.models import Sale
from purchases.models import Purchase

from ledger.models import LedgerEntry
from cashbook.models import CashbookEntry


# ======================================================
# PAYMENT NUMBER GENERATOR
# ======================================================

def _generate_payment_no():
    """
    Generates sequential payment number:
    PAY-000001, PAY-000002 ...
    """

    last_payment = Payment.objects.order_by("-id").first()

    if not last_payment:
        return "PAY-000001"

    try:
        last_no = int(last_payment.payment_no.split("-")[1])
    except Exception:
        last_no = last_payment.id

    return f"PAY-{last_no + 1:06d}"


# ======================================================
# VALIDATION HELPERS
# ======================================================

def _validate_amount(amount):
    amount = Decimal(str(amount))

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    return amount


# ======================================================
# LEDGER HELPERS
# ======================================================

def _customer_ledger(payment, description):
    LedgerEntry.objects.create(
        party_type="CUSTOMER",
        customer=payment.customer,
        reference_type="PAYMENT",
        reference_no=payment.payment_no,
        debit=Decimal("0.00"),
        credit=payment.amount,
        description=description,
        date=payment.payment_date,
    )


def _supplier_ledger(payment, description):
    LedgerEntry.objects.create(
        party_type="SUPPLIER",
        supplier=payment.supplier,
        reference_type="PAYMENT",
        reference_no=payment.payment_no,
        debit=payment.amount,
        credit=Decimal("0.00"),
        description=description,
        date=payment.payment_date,
    )


# ======================================================
# CASHBOOK HELPER
# ======================================================

def _cashbook_entry(entry_type, source_type, payment, description):
    """
    entry_type: IN / OUT
    source_type: SALE / PURCHASE / OTHER
    """

    CashbookEntry.objects.create(
        entry_type=entry_type,
        source_type=source_type,
        amount=payment.amount,
        reference=payment.payment_no,
        description=description,
        date=payment.payment_date,
    )


# ======================================================
# SALE / PURCHASE UPDATE HELPERS
# ======================================================

def _update_sale_payment(sale):
    total_paid = (
        Payment.objects.filter(sale=sale)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    sale.paid_amount = total_paid
    sale.due_amount = sale.total_amount - total_paid

    if sale.due_amount <= 0:
        sale.status = "PAID"
        sale.due_amount = Decimal("0.00")
    elif total_paid > 0:
        sale.status = "PARTIAL"
    else:
        sale.status = "UNPAID"

    sale.save()


def _update_purchase_payment(purchase):
    total_paid = (
        Payment.objects.filter(purchase=purchase)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    purchase.paid_amount = total_paid
    purchase.due_amount = purchase.total_amount - total_paid

    if purchase.due_amount <= 0:
        purchase.status = "PAID"
        purchase.due_amount = Decimal("0.00")
    elif total_paid > 0:
        purchase.status = "PARTIAL"
    else:
        purchase.status = "UNPAID"

    purchase.save()


# ======================================================
# CUSTOMER PAYMENT AGAINST SALE
# ======================================================

@transaction.atomic
def receive_customer_payment(
    sale,
    amount,
    payment_date,
    payment_method="CASH",
    received_by=None,
    transaction_id="",
    reference_no="",
    note=""
):
    """
    Customer pays against an invoice (SALE PAYMENT)
    """

    amount = _validate_amount(amount)

    if not sale:
        raise ValueError("Sale is required for customer invoice payment.")

    if amount > sale.due_amount:
        raise ValueError("Payment cannot exceed due amount.")

    customer = sale.customer

    payment = Payment.objects.create(
        payment_no=_generate_payment_no(),
        payment_type="CUSTOMER",
        customer=customer,
        sale=sale,
        supplier=None,
        purchase=None,
        amount=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        payment_date=payment_date,
        received_by=received_by,
        reference_no=reference_no,
        note=note,
    )

    # update invoice
    _update_sale_payment(sale)

    # ledger
    _customer_ledger(
        payment,
        description=f"Invoice Payment {sale.invoice_no}"
    )

    # cashbook
    _cashbook_entry(
        entry_type="IN",
        source_type="SALE",
        payment=payment,
        description="Customer Invoice Payment"
    )

    return payment


# ======================================================
# CUSTOMER ADVANCE PAYMENT
# ======================================================

@transaction.atomic
def receive_customer_advance(
    customer,
    amount,
    payment_date,
    payment_method="CASH",
    received_by=None,
    transaction_id="",
    reference_no="",
    note=""
):
    """
    Customer pays without invoice (ADVANCE PAYMENT)
    """

    amount = _validate_amount(amount)

    if not customer:
        raise ValueError("Customer is required for advance payment.")

    payment = Payment.objects.create(
        payment_no=_generate_payment_no(),
        payment_type="CUSTOMER",
        customer=customer,
        sale=None,
        supplier=None,
        purchase=None,
        amount=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        payment_date=payment_date,
        received_by=received_by,
        reference_no=reference_no,
        note=note,
    )

    # ledger (advance = credit customer)
    _customer_ledger(
        payment,
        description="Customer Advance Payment"
    )

    # cashbook
    _cashbook_entry(
        entry_type="IN",
        source_type="OTHER",
        payment=payment,
        description="Customer Advance Payment"
    )

    return payment


# ======================================================
# SUPPLIER PAYMENT AGAINST PURCHASE
# ======================================================

@transaction.atomic
def pay_supplier(
    purchase,
    amount,
    payment_date,
    payment_method="CASH",
    received_by=None,
    transaction_id="",
    reference_no="",
    note=""
):
    """
    Supplier payment against PURCHASE invoice
    """

    amount = _validate_amount(amount)

    if not purchase:
        raise ValueError("Purchase is required for supplier payment.")

    if amount > purchase.due_amount:
        raise ValueError("Payment cannot exceed due amount.")

    supplier = purchase.supplier

    payment = Payment.objects.create(
        payment_no=_generate_payment_no(),
        payment_type="SUPPLIER",
        customer=None,
        supplier=supplier,
        sale=None,
        purchase=purchase,
        amount=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        payment_date=payment_date,
        received_by=received_by,
        reference_no=reference_no,
        note=note,
    )

    # update purchase
    _update_purchase_payment(purchase)

    # ledger (supplier = debit)
    _supplier_ledger(
        payment,
        description=f"Purchase Payment {purchase.invoice_no}"
    )

    # cashbook OUT
    _cashbook_entry(
        entry_type="OUT",
        source_type="PURCHASE",
        payment=payment,
        description="Supplier Invoice Payment"
    )

    return payment


# ======================================================
# SUPPLIER ADVANCE PAYMENT
# ======================================================

@transaction.atomic
def supplier_advance_payment(
    supplier,
    amount,
    payment_date,
    payment_method="CASH",
    received_by=None,
    transaction_id="",
    reference_no="",
    note=""
):
    """
    Supplier advance payment (without purchase invoice)
    """

    amount = _validate_amount(amount)

    if not supplier:
        raise ValueError("Supplier is required for advance payment.")

    payment = Payment.objects.create(
        payment_no=_generate_payment_no(),
        payment_type="SUPPLIER",
        customer=None,
        supplier=supplier,
        sale=None,
        purchase=None,
        amount=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        payment_date=payment_date,
        received_by=received_by,
        reference_no=reference_no,
        note=note,
    )

    # ledger (supplier advance = debit)
    _supplier_ledger(
        payment,
        description="Supplier Advance Payment"
    )

    # cashbook OUT
    _cashbook_entry(
        entry_type="OUT",
        source_type="OTHER",
        payment=payment,
        description="Supplier Advance Payment"
    )

    return payment