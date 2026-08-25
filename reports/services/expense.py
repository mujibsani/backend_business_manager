from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncMonth

from expenses.models import Expense


def get_expense_summary():

    total = (
        Expense.objects
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return {
        "total": total,
    }


def get_daily_expenses():

    return list(
        Expense.objects
        .annotate(period=TruncDate("date"))
        .values("period")
        .annotate(total=Sum("amount"))
        .order_by("period")
    )


def get_monthly_expenses():

    return list(
        Expense.objects
        .annotate(period=TruncMonth("date"))
        .values("period")
        .annotate(total=Sum("amount"))
        .order_by("period")
    )