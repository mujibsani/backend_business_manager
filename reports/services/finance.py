from decimal import Decimal

from django.db.models import Sum

from sales.models import Sale
from purchases.models import Purchase
from expenses.models import Expense
from cashbook.models import CashbookEntry


def get_profit_summary():

    sales = (
        Sale.objects
        .aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )

    purchases = (
        Purchase.objects
        .aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )

    expenses = (
        Expense.objects
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    gross_profit = sales - purchases
    net_profit = gross_profit - expenses

    return {
        "sales": sales,
        "purchases": purchases,
        "expenses": expenses,
        "gross_profit": gross_profit,
        "net_profit": net_profit,
    }


def get_cash_flow_summary():

    cash_in = (
        CashbookEntry.objects
        .filter(entry_type="IN")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    cash_out = (
        CashbookEntry.objects
        .filter(entry_type="OUT")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return {
        "cash_in": cash_in,
        "cash_out": cash_out,
        "balance": cash_in - cash_out,
    }