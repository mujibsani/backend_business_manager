from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db.models import Sum

from .models import CashbookEntry


# ==========================================================
# DECIMAL HELPER
# ==========================================================

def _to_decimal(value):
    try:
        return Decimal(str(value))
    except (TypeError, ValueError, InvalidOperation):
        raise ValidationError(
            "Invalid cashbook amount."
        )


# ==========================================================
# INTERNAL CREATE
# ==========================================================

def _create_cashbook_entry(
    *,
    entry_type,
    source_type,
    amount,
    date,
    reference="",
    description="",
):

    amount = _to_decimal(amount)

    if amount <= Decimal("0.00"):

        raise ValidationError(
            "Cashbook amount must be greater than zero."
        )

    if entry_type not in dict(
        CashbookEntry.ENTRY_TYPE
    ):

        raise ValidationError(
            "Invalid cashbook entry type."
        )

    if source_type not in dict(
        CashbookEntry.SOURCE_TYPE
    ):

        raise ValidationError(
            "Invalid cashbook source type."
        )

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

    return _create_cashbook_entry(
        entry_type="OUT",
        source_type=source_type,
        amount=amount,
        date=date,
        reference=reference,
        description=description,
    )


# ==========================================================
# CASHBOOK SUMMARY
# ==========================================================

def get_cashbook_summary():

    total_in = (
        CashbookEntry.objects
        .filter(entry_type="IN")
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    total_out = (
        CashbookEntry.objects
        .filter(entry_type="OUT")
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    return {
        "cash_in": total_in,
        "cash_out": total_out,
        "balance": total_in - total_out,
    }