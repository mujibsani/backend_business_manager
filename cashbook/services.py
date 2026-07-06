from .models import CashbookEntry
from django.db.models import Sum

from .models import CashbookEntry


def create_cashbook_entry(entry_type, source_type, amount, reference="", description=""):
    return CashbookEntry.objects.create(
        entry_type=entry_type,
        source_type=source_type,
        amount=amount,
        reference=reference,
        description=description
    )

def get_cashbook_summary():

    total_in = CashbookEntry.objects.filter(entry_type="IN").aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_out = CashbookEntry.objects.filter(entry_type="OUT").aggregate(
        total=Sum("amount")
    )["total"] or 0

    balance = total_in - total_out

    return {
        "cash_in": total_in,
        "cash_out": total_out,
        "balance": balance
    }

