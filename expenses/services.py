from django.db import transaction

from cashbook.models import CashbookEntry

from .models import Expense


# ==========================================================
# CREATE EXPENSE
# ==========================================================

@transaction.atomic
def create_expense(
    category,
    amount,
    date,
    description="",
):

    expense = Expense.objects.create(
        category=category,
        amount=amount,
        date=date,
        description=description,
    )

    CashbookEntry.objects.create(
        entry_type="OUT",
        source_type="EXPENSE",
        amount=expense.amount,
        reference=f"EXP-{expense.id}",
        description=expense.description,
        date=expense.date,
    )

    return expense


# ==========================================================
# UPDATE EXPENSE
# ==========================================================

@transaction.atomic
def update_expense(
    expense,
    category,
    amount,
    date,
    description="",
):

    expense.category = category
    expense.amount = amount
    expense.date = date
    expense.description = description
    expense.save()

    CashbookEntry.objects.update_or_create(
        source_type="EXPENSE",
        reference=f"EXP-{expense.id}",
        defaults={
            "entry_type": "OUT",
            "amount": expense.amount,
            "description": expense.description,
            "date": expense.date,
        },
    )

    return expense


# ==========================================================
# DELETE EXPENSE
# ==========================================================

@transaction.atomic
def delete_expense(expense):

    CashbookEntry.objects.filter(
        source_type="EXPENSE",
        reference=f"EXP-{expense.id}",
    ).delete()

    expense.delete()