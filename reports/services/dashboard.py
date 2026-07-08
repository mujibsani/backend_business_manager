from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone

from sales.models import Sale
from purchases.models import Purchase
from expenses.models import Expense
from products.models import Product
from customers.models import Customer
from suppliers.models import Supplier
from cashbook.models import CashbookEntry


# ==========================================================
# TODAY SUMMARY
# ==========================================================

def get_today_summary():

    today = timezone.localdate()

    sales = (
        Sale.objects.filter(date=today)
        .aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )

    purchases = (
        Purchase.objects.filter(date=today)
        .aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )

    expenses = (
        Expense.objects.filter(date=today)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return {
        "sales": sales,
        "purchases": purchases,
        "expenses": expenses,
    }


# ==========================================================
# MONTH SUMMARY
# ==========================================================

def get_month_summary():

    today = timezone.localdate()

    sales = (
        Sale.objects.filter(
            date__year=today.year,
            date__month=today.month,
        ).aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )

    purchases = (
        Purchase.objects.filter(
            date__year=today.year,
            date__month=today.month,
        ).aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )

    expenses = (
        Expense.objects.filter(
            date__year=today.year,
            date__month=today.month,
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return {
        "sales": sales,
        "purchases": purchases,
        "expenses": expenses,
    }


# ==========================================================
# CASH SUMMARY
# ==========================================================

def get_cash_summary():

    cash_in = (
        CashbookEntry.objects.filter(entry_type="IN")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    cash_out = (
        CashbookEntry.objects.filter(entry_type="OUT")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return {
        "cash_in": cash_in,
        "cash_out": cash_out,
        "cash_balance": cash_in - cash_out,
    }


# ==========================================================
# INVENTORY SUMMARY
# ==========================================================

def get_inventory_summary():

    inventory = Product.objects.aggregate(
        inventory_value=Sum(
            models.F("stock") * models.F("cost_price"),
            output_field=models.DecimalField(max_digits=20, decimal_places=2),
        )
    )

    low_stock = Product.objects.filter(
        stock__lte=models.F("min_stock")
    ).count()

    return {
        "inventory_value": inventory["inventory_value"] or Decimal("0.00"),
        "low_stock_products": low_stock,
        "total_products": Product.objects.count(),
    }


# ==========================================================
# PARTY SUMMARY
# ==========================================================

def get_party_summary():

    customer_due = (
        Sale.objects.aggregate(total=Sum("due_amount"))["total"]
        or Decimal("0.00")
    )

    supplier_due = (
        Purchase.objects.aggregate(total=Sum("due_amount"))["total"]
        or Decimal("0.00")
    )

    return {
        "customer_due": customer_due,
        "supplier_due": supplier_due,
        "customers": Customer.objects.count(),
        "suppliers": Supplier.objects.count(),
    }


# ==========================================================
# COMPLETE DASHBOARD
# ==========================================================

def get_dashboard_summary():

    return {
        "today": get_today_summary(),
        "month": get_month_summary(),
        "cash": get_cash_summary(),
        "inventory": get_inventory_summary(),
        "parties": get_party_summary(),
    }