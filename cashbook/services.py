from decimal import Decimal

from django.db.models import Sum

from .models import CashbookEntry


def _create_cashbook_entry(
    *,
    entry_type,
    source_type,
    amount,
    date,
    reference="",
    description="",
):
    """
    Internal helper.
    All cashbook entries should be created through this function.
    """

    return CashbookEntry.objects.create(
        entry_type=entry_type,
        source_type=source_type,
        amount=amount,
        date=date,
        reference=reference,
        description=description,
    )


# ==========================================================
# CASH IN
# ==========================================================

def cash_in(
    amount,
    source_type,
    date,
    reference="",
    description="",
):
    """
    Record incoming cash.
    Example:
        - Customer Payment
        - Cash Sale
        - Other Income
    """

    return _create_cashbook_entry(
        entry_type="IN",
        source_type=source_type,
        amount=amount,
        date=date,
        reference=reference,
        description=description,
    )


# ==========================================================
# CASH OUT
# ==========================================================

def cash_out(
    amount,
    source_type,
    date,
    reference="",
    description="",
):
    """
    Record outgoing cash.
    Example:
        - Supplier Payment
        - Expense
        - Other Expense
    """

    return _create_cashbook_entry(
        entry_type="OUT",
        source_type=source_type,
        amount=amount,
        date=date,
        reference=reference,
        description=description,
    )


# ==========================================================
# SUMMARY
# ==========================================================

def get_cashbook_summary():

    total_in = (
        CashbookEntry.objects.filter(
            entry_type="IN"
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    total_out = (
        CashbookEntry.objects.filter(
            entry_type="OUT"
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    return {
        "cash_in": total_in,
        "cash_out": total_out,
        "balance": total_in - total_out,
    }