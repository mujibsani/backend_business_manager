from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Expense

from cashbook.services import cash_out


@transaction.atomic
def create_expense(
    *,
    category,
    amount,
    date,
    description="",
    created_by=None,
):
    """
    Create a business expense.

    Accounting Flow

        Expense
            ↓
        Cashbook (OUT)

    Future:
        Journal Entry
    """

    if amount <= 0:
        raise ValidationError("Expense amount must be greater than zero.")

    expense = Expense.objects.create(
        category=category,
        amount=amount,
        date=date,
        description=description,
        created_by=created_by,
    )

    process_expense_accounting(expense)

    return expense


def process_expense_accounting(expense):
    """
    Create accounting entries after an expense is created.
    """

    cash_out(
        amount=expense.amount,
        source_type="EXPENSE",
        date=expense.date,
        reference=f"EXP-{expense.id}",
        description=expense.description or expense.category.name,
    )
