from decimal import Decimal

from .models import LedgerEntry


# ==========================================================
# LEDGER POSTING FUNCTIONS
# ==========================================================

def customer_sale(customer, sale):
    """
    Create customer ledger entry when a sale invoice is created.
    """

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
    """
    Create customer ledger entry when payment is received.
    """

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
    """
    Create supplier ledger entry when a purchase invoice is created.
    """

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
    """
    Create supplier ledger entry when supplier is paid.
    """

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


# ==========================================================
# CUSTOMER LEDGER STATEMENT
# ==========================================================

def get_customer_statement(customer, from_date=None, to_date=None):
    """
    Returns customer ledger statement with opening balance,
    running balance and closing balance.
    """

    entries = LedgerEntry.objects.filter(
        customer=customer
    ).order_by("date", "id")

    opening_balance = customer.opening_balance

    if customer.opening_balance_type == "PAYABLE":
        opening_balance *= Decimal("-1")

    if from_date:

        previous_entries = entries.filter(
            date__lt=from_date
        )

        for entry in previous_entries:
            opening_balance += entry.debit
            opening_balance -= entry.credit

        entries = entries.filter(
            date__gte=from_date
        )

    if to_date:
        entries = entries.filter(
            date__lte=to_date
        )

    running_balance = opening_balance

    statement = []

    for entry in entries:

        running_balance += entry.debit
        running_balance -= entry.credit

        statement.append({
            "date": entry.date,
            "reference_type": entry.reference_type,
            "reference_no": entry.reference_no,
            "description": entry.description,
            "debit": entry.debit,
            "credit": entry.credit,
            "balance": running_balance,
        })

    return {
        "party": customer,
        "opening_balance": opening_balance,
        "closing_balance": running_balance,
        "transactions": statement,
    }


# ==========================================================
# SUPPLIER LEDGER STATEMENT
# ==========================================================

def get_supplier_statement(supplier, from_date=None, to_date=None):
    """
    Returns supplier ledger statement with opening balance,
    running balance and closing balance.
    """

    entries = LedgerEntry.objects.filter(
        supplier=supplier
    ).order_by("date", "id")

    opening_balance = supplier.opening_balance

    if supplier.opening_balance_type == "ADVANCE":
        opening_balance *= Decimal("-1")

    if from_date:

        previous_entries = entries.filter(
            date__lt=from_date
        )

        for entry in previous_entries:
            opening_balance += entry.debit
            opening_balance -= entry.credit

        entries = entries.filter(
            date__gte=from_date
        )

    if to_date:
        entries = entries.filter(
            date__lte=to_date
        )

    running_balance = opening_balance

    statement = []

    for entry in entries:

        running_balance += entry.debit
        running_balance -= entry.credit

        statement.append({
            "date": entry.date,
            "reference_type": entry.reference_type,
            "reference_no": entry.reference_no,
            "description": entry.description,
            "debit": entry.debit,
            "credit": entry.credit,
            "balance": running_balance,
        })

    return {
        "party": supplier,
        "opening_balance": opening_balance,
        "closing_balance": running_balance,
        "transactions": statement,
    }