from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth

from purchases.models import Purchase


def get_purchase_summary():
    """
    Overall purchase summary.
    """

    total = (
        Purchase.objects.aggregate(
            total=Sum("total_amount")
        )["total"]
        or Decimal("0.00")
    )

    paid = (
        Purchase.objects.aggregate(
            total=Sum("paid_amount")
        )["total"]
        or Decimal("0.00")
    )

    due = (
        Purchase.objects.aggregate(
            total=Sum("due_amount")
        )["total"]
        or Decimal("0.00")
    )

    return {
        "total": total,
        "paid": paid,
        "due": due,
    }


def get_daily_purchases():
    data = (
        Purchase.objects
        .annotate(day=TruncDate("date"))
        .values("day")
        .annotate(total=Sum("total_amount"))
        .order_by("day")
    )

    return list(data)


def get_weekly_purchases():
    data = (
        Purchase.objects
        .annotate(week=TruncWeek("date"))
        .values("week")
        .annotate(total=Sum("total_amount"))
        .order_by("week")
    )

    return list(data)


def get_monthly_purchases():
    data = (
        Purchase.objects
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )

    return list(data)