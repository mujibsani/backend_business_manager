from decimal import Decimal

from django.db.models import Sum

from .models import LedgerEntry


# ==========================================================
# INTERNAL LEDGER ENTRY HELPER
# ==========================================================

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

    LedgerEntry.save() automatically calculates the running
    balance:

        balance = previous_balance + debit - credit
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
# CUSTOMER LEDGER
# ==========================================================

def create_customer_sale_entry(
    customer,
    sale,
):
    """
    Customer purchased goods.

    Customer owes money.

    Therefore:
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


def create_customer_payment_entry(
    customer,
    amount,
    reference_no,
    date,
):
    """
    Customer paid money.

    Customer receivable decreases.

    Therefore:
        Credit customer ledger.
    """

    amount = Decimal(str(amount))

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
    Customer ledger adjustment.

    Positive amount:
        Debit

    Negative amount:
        Credit
    """

    amount = Decimal(str(amount))

    if amount >= Decimal("0.00"):
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


def create_customer_sales_return_entry(
    customer,
    sales_return,
):
    """
    Customer returned goods.

    This reduces the amount receivable from the customer.

    Therefore:
        Credit customer ledger.
    """

    return _create_entry(
        party_type="CUSTOMER",
        customer=customer,
        reference_type="SALE_RETURN",
        reference_no=sales_return.return_no,
        debit=Decimal("0.00"),
        credit=sales_return.total_amount,
        description=(
            f"Sales Return {sales_return.return_no}"
        ),
        date=sales_return.date,
    )


# ==========================================================
# SUPPLIER LEDGER
# ==========================================================

def create_supplier_purchase_entry(
    supplier,
    purchase,
):
    """
    Purchased goods from supplier.

    Business owes supplier money.

    Therefore:
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
    Business paid supplier.

    Supplier payable decreases.

    Therefore:
        Debit supplier ledger.
    """

    amount = Decimal(str(amount))

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
    Supplier ledger adjustment.

    Positive amount:
        Debit

    Negative amount:
        Credit
    """

    amount = Decimal(str(amount))

    if amount >= Decimal("0.00"):
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


def create_supplier_purchase_return_entry(
    supplier,
    purchase_return,
):
    """
    Supplier purchase return.

    Returning purchased goods reduces the amount
    payable to the supplier.

    Therefore:
        Debit = Purchase Return amount
        Credit = 0

    The supplier's cash refund, if any, is recorded
    separately in the cashbook as CASH IN.

    Example:

        Supplier balance before return = 10,000

        Purchase Return:
            Debit  = 2,000
            Credit = 0

        New supplier balance = 8,000
    """

    return _create_entry(
        party_type="SUPPLIER",
        supplier=supplier,
        reference_type="PURCHASE_RETURN",
        reference_no=purchase_return.return_no,
        debit=purchase_return.total_amount,
        credit=Decimal("0.00"),
        description=(
            f"Purchase Return {purchase_return.return_no}"
        ),
        date=purchase_return.date,
    )


# ==========================================================
# CUSTOMER STATEMENT
# ==========================================================

def get_customer_statement(
    customer,
    from_date=None,
    to_date=None,
):
    """
    Return customer ledger statement.

    Opening balance:
        Total debit - total credit
        before from_date.
    """

    queryset = (
        LedgerEntry.objects
        .filter(customer=customer)
        .order_by("date", "id")
    )

    opening_balance = Decimal("0.00")

    # ------------------------------------------------------
    # OPENING BALANCE
    # ------------------------------------------------------

    if from_date:

        previous = queryset.filter(
            date__lt=from_date
        )

        debit_total = (
            previous.aggregate(
                total=Sum("debit")
            )["total"]
            or Decimal("0.00")
        )

        credit_total = (
            previous.aggregate(
                total=Sum("credit")
            )["total"]
            or Decimal("0.00")
        )

        opening_balance = (
            debit_total - credit_total
        )

        queryset = queryset.filter(
            date__gte=from_date
        )

    # ------------------------------------------------------
    # END DATE
    # ------------------------------------------------------

    if to_date:

        queryset = queryset.filter(
            date__lte=to_date
        )

    # ------------------------------------------------------
    # TRANSACTIONS
    # ------------------------------------------------------

    transactions = list(
        queryset.values(
            "date",
            "reference_type",
            "reference_no",
            "description",
            "debit",
            "credit",
            "balance",
        )
    )

    # ------------------------------------------------------
    # CLOSING BALANCE
    # ------------------------------------------------------

    last_entry = queryset.last()

    if last_entry:
        closing_balance = last_entry.balance
    else:
        closing_balance = opening_balance

    return {
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "transactions": transactions,
    }


# ==========================================================
# SUPPLIER STATEMENT
# ==========================================================

def get_supplier_statement(
    supplier,
    from_date=None,
    to_date=None,
):
    """
    Return supplier ledger statement.

    Opening balance:
        Total debit - total credit
        before from_date.
    """

    queryset = (
        LedgerEntry.objects
        .filter(supplier=supplier)
        .order_by("date", "id")
    )

    opening_balance = Decimal("0.00")

    # ------------------------------------------------------
    # OPENING BALANCE
    # ------------------------------------------------------

    if from_date:

        previous = queryset.filter(
            date__lt=from_date
        )

        debit_total = (
            previous.aggregate(
                total=Sum("debit")
            )["total"]
            or Decimal("0.00")
        )

        credit_total = (
            previous.aggregate(
                total=Sum("credit")
            )["total"]
            or Decimal("0.00")
        )

        opening_balance = (
            debit_total - credit_total
        )

        queryset = queryset.filter(
            date__gte=from_date
        )

    # ------------------------------------------------------
    # END DATE
    # ------------------------------------------------------

    if to_date:

        queryset = queryset.filter(
            date__lte=to_date
        )

    # ------------------------------------------------------
    # TRANSACTIONS
    # ------------------------------------------------------

    transactions = list(
        queryset.values(
            "date",
            "reference_type",
            "reference_no",
            "description",
            "debit",
            "credit",
            "balance",
        )
    )

    # ------------------------------------------------------
    # CLOSING BALANCE
    # ------------------------------------------------------

    last_entry = queryset.last()

    if last_entry:
        closing_balance = last_entry.balance
    else:
        closing_balance = opening_balance

    return {
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "transactions": transactions,
    }