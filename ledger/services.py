from decimal import Decimal
from django.db.models import Sum
from .models import LedgerEntry


def _create_entry(
    *,
    party_type,
    customer=None,
    supplier=None,
    reference_type,
    reference_no,
    debit=Decimal("0.00"),
    credit=Decimal("0.00"),
    description="",
    date,
):
    """
    Internal helper.
    All ledger entries should be created through this function.
    """

    return LedgerEntry.objects.create(
        party_type=party_type,
        customer=customer,
        supplier=supplier,
        reference_type=reference_type,
        reference_no=reference_no,
        debit=debit,
        credit=credit,
        description=description,
        date=date,
    )


# ==========================================================
# CUSTOMER
# ==========================================================

def create_customer_sale_entry(customer, sale):
    """
    Customer purchased goods.
    Customer owes money.
    Debit customer ledger.
    """

    return _create_entry(
        party_type="CUSTOMER",
        customer=customer,
        reference_type="SALE",
        reference_no=sale.invoice_no,
        debit=sale.total_amount,
        credit=Decimal("0.00"),
        description=f"Sale Invoice {sale.invoice_no}",
        date=sale.date,
    )


def create_customer_payment_entry(customer, amount, reference_no, date):
    """
    Customer paid money.
    Reduce customer receivable.
    """

    return _create_entry(
        party_type="CUSTOMER",
        customer=customer,
        reference_type="PAYMENT",
        reference_no=reference_no,
        debit=Decimal("0.00"),
        credit=amount,
        description="Customer Payment",
        date=date,
    )


def create_customer_adjustment_entry(
    customer,
    amount,
    reference_no,
    date,
    description,
):
    """
    Positive amount = Debit
    Negative amount = Credit
    """

    if amount >= 0:
        debit = amount
        credit = Decimal("0.00")
    else:
        debit = Decimal("0.00")
        credit = abs(amount)

    return _create_entry(
        party_type="CUSTOMER",
        customer=customer,
        reference_type="ADJUSTMENT",
        reference_no=reference_no,
        debit=debit,
        credit=credit,
        description=description,
        date=date,
    )


# ==========================================================
# SUPPLIER
# ==========================================================

def create_supplier_purchase_entry(supplier, purchase):
    """
    Purchased goods from supplier.
    Business owes supplier.
    Credit supplier ledger.
    """

    return _create_entry(
        party_type="SUPPLIER",
        supplier=supplier,
        reference_type="PURCHASE",
        reference_no=purchase.invoice_no,
        debit=Decimal("0.00"),
        credit=purchase.total_amount,
        description=f"Purchase Invoice {purchase.invoice_no}",
        date=purchase.date,
    )


def create_supplier_payment_entry(
    supplier,
    amount,
    reference_no,
    date,
):
    """
    Paid supplier.
    Reduce supplier payable.
    """

    return _create_entry(
        party_type="SUPPLIER",
        supplier=supplier,
        reference_type="PAYMENT",
        reference_no=reference_no,
        debit=amount,
        credit=Decimal("0.00"),
        description="Supplier Payment",
        date=date,
    )


def create_supplier_adjustment_entry(
    supplier,
    amount,
    reference_no,
    date,
    description,
):
    """
    Positive amount = Debit
    Negative amount = Credit
    """

    if amount >= 0:
        debit = amount
        credit = Decimal("0.00")
    else:
        debit = Decimal("0.00")
        credit = abs(amount)

    return _create_entry(
        party_type="SUPPLIER",
        supplier=supplier,
        reference_type="ADJUSTMENT",
        reference_no=reference_no,
        debit=debit,
        credit=credit,
        description=description,
        date=date,
    )



# ======================================================
# CUstomer Statement
# ======================================================
def get_customer_statement(customer, from_date=None, to_date=None):

    queryset = LedgerEntry.objects.filter(
        customer=customer
    ).order_by("date", "id")

    opening_balance = Decimal("0.00")

    if from_date:
        previous = queryset.filter(date__lt=from_date)

        debit_total = (
            previous.aggregate(total=Sum("debit"))["total"]
            or Decimal("0.00")
        )

        credit_total = (
            previous.aggregate(total=Sum("credit"))["total"]
            or Decimal("0.00")
        )

        opening_balance = debit_total - credit_total

        queryset = queryset.filter(date__gte=from_date)

    if to_date:
        queryset = queryset.filter(date__lte=to_date)

    transactions = list(queryset.values(
        "date",
        "reference_type",
        "reference_no",
        "description",
        "debit",
        "credit",
        "balance",
    ))

    closing_balance = (
        queryset.last().balance
        if queryset.exists()
        else opening_balance
    )

    return {
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "transactions": transactions,
    }



# ======================================================
# Supplier Statement
# ======================================================
def get_supplier_statement(supplier, from_date=None, to_date=None):

    queryset = LedgerEntry.objects.filter(
        supplier=supplier
    ).order_by("date", "id")

    opening_balance = Decimal("0.00")

    if from_date:

        previous = queryset.filter(date__lt=from_date)

        debit_total = (
            previous.aggregate(total=Sum("debit"))["total"]
            or Decimal("0.00")
        )

        credit_total = (
            previous.aggregate(total=Sum("credit"))["total"]
            or Decimal("0.00")
        )

        opening_balance = debit_total - credit_total

        queryset = queryset.filter(date__gte=from_date)

    if to_date:
        queryset = queryset.filter(date__lte=to_date)

    transactions = list(queryset.values(
        "date",
        "reference_type",
        "reference_no",
        "description",
        "debit",
        "credit",
        "balance",
    ))

    closing_balance = (
        queryset.last().balance
        if queryset.exists()
        else opening_balance
    )

    return {
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "transactions": transactions,
    }



def create_customer_sales_return_entry(
    customer,
    sales_return,
):
    """
    Customer returned goods.

    Reduce customer's receivable.

    Credit customer ledger.
    """

    return _create_entry(
        party_type="CUSTOMER",
        customer=customer,
        reference_type="SALE_RETURN",
        reference_no=sales_return.return_no,
        debit=Decimal("0.00"),
        credit=sales_return.total_amount,
        description=f"Sales Return {sales_return.return_no}",
        date=sales_return.date,
    )
