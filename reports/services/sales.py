from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth

from sales.models import Sale


def get_sales_summary():
    total = (
        Sale.objects
        .aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )

    paid = (
        Sale.objects
        .aggregate(total=Sum("paid_amount"))["total"]
        or Decimal("0.00")
    )

    due = (
        Sale.objects
        .aggregate(total=Sum("due_amount"))["total"]
        or Decimal("0.00")
    )

    return {
        "total": total,
        "paid": paid,
        "due": due,
    }


def get_daily_sales():
    return list(
        Sale.objects
        .annotate(period=TruncDate("date"))
        .values("period")
        .annotate(total=Sum("total_amount"))
        .order_by("period")
    )


def get_weekly_sales():
    return list(
        Sale.objects
        .annotate(period=TruncWeek("date"))
        .values("period")
        .annotate(total=Sum("total_amount"))
        .order_by("period")
    )


def get_monthly_sales():
    return list(
        Sale.objects
        .annotate(period=TruncMonth("date"))
        .values("period")
        .annotate(total=Sum("total_amount"))
        .order_by("period")
    )