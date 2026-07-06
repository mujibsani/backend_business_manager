from decimal import Decimal

from .models import LedgerEntry


def customer_sale(customer, sale):

    LedgerEntry.objects.create(
        party_type="CUSTOMER",
        customer=customer,
        reference_type="SALE",
        reference_no=sale.invoice_no,
        debit=sale.total_amount,
        credit=Decimal("0.00"),
        description=f"Sale Invoice {sale.invoice_no}",
        date=sale.date,
    )


def customer_payment(customer, amount, reference_no, date):

    LedgerEntry.objects.create(
        party_type="CUSTOMER",
        customer=customer,
        reference_type="PAYMENT",
        reference_no=reference_no,
        debit=Decimal("0.00"),
        credit=amount,
        description="Customer Payment",
        date=date,
    )


def supplier_purchase(supplier, purchase):

    LedgerEntry.objects.create(
        party_type="SUPPLIER",
        supplier=supplier,
        reference_type="PURCHASE",
        reference_no=purchase.invoice_no,
        debit=Decimal("0.00"),
        credit=purchase.total_amount,
        description=f"Purchase Invoice {purchase.invoice_no}",
        date=purchase.date,
    )


def supplier_payment(supplier, amount, reference_no, date):

    LedgerEntry.objects.create(
        party_type="SUPPLIER",
        supplier=supplier,
        reference_type="PAYMENT",
        reference_no=reference_no,
        debit=amount,
        credit=Decimal("0.00"),
        description="Supplier Payment",
        date=date,
    )