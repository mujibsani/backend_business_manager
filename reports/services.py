from django.db.models import Sum, F

from sales.models import Sale
from purchases.models import Purchase
from payments.models import Payment
from products.models import Product

from django.db.models.functions import TruncDate
from django.db.models.functions import TruncWeek
from django.db.models.functions import TruncMonth

def get_dashboard_data():

    # ------------------------
    # TOTAL SALES
    # ------------------------
    total_sales = Sale.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    total_paid_sales = Sale.objects.aggregate(
        total=Sum("paid_amount")
    )["total"] or 0

    total_due_sales = Sale.objects.aggregate(
        total=Sum("due_amount")
    )["total"] or 0


    # ------------------------
    # TOTAL PURCHASES
    # ------------------------
    total_purchase = Purchase.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    total_paid_purchase = Purchase.objects.aggregate(
        total=Sum("paid_amount")
    )["total"] or 0

    total_due_purchase = Purchase.objects.aggregate(
        total=Sum("due_amount")
    )["total"] or 0


    # ------------------------
    # CASH FLOW
    # ------------------------
    cash_in = total_paid_sales
    cash_out = total_paid_purchase

    cash_balance = cash_in - cash_out


    # ------------------------
    # LOW STOCK PRODUCTS
    # ------------------------
    low_stock_products = Product.objects.filter(
        stock__lte=F("min_stock")
    ).values("id", "name", "stock", "min_stock")


    # ------------------------
    # TOP PRODUCTS (simple version)
    # ------------------------
    top_products = Product.objects.order_by("-stock")[:5].values(
        "id", "name", "stock"
    )


    return {
        "sales": {
            "total": total_sales,
            "paid": total_paid_sales,
            "due": total_due_sales,
        },
        "purchases": {
            "total": total_purchase,
            "paid": total_paid_purchase,
            "due": total_due_purchase,
        },
        "cash": {
            "in": cash_in,
            "out": cash_out,
            "balance": cash_balance,
        },
        "alerts": {
            "low_stock": list(low_stock_products),
        },
        "top_products": list(top_products),
    }

def get_profit_summary():

    total_sales = Sale.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    total_purchase = Purchase.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    profit = total_sales - total_purchase

    return {
        "total_sales": total_sales,
        "total_purchase": total_purchase,
        "profit": profit
    }

def get_daily_sales():

    data = (
        Sale.objects
        .annotate(date=TruncDate("date"))
        .values("date")
        .annotate(total=Sum("total_amount"))
        .order_by("date")
    )

    return list(data)


def get_weekly_sales():

    data = (
        Sale.objects
        .annotate(week=TruncWeek("date"))
        .values("week")
        .annotate(total=Sum("total_amount"))
        .order_by("week")
    )

    return list(data)


def get_monthly_sales():

    data = (
        Sale.objects
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )

    return list(data)

