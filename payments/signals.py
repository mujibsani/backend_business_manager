from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment
from sales.models import Sale
from purchases.models import Purchase
from cashbook.models import CashbookEntry
from ledger.models import LedgerEntry


@receiver(post_save, sender=Payment)
def handle_payment(sender, instance, created, **kwargs):

    if not created:
        return

    # -------------------------
    # 1. SALE PAYMENT
    # -------------------------
    if instance.type == "SALE" and instance.sale:

        sale = instance.sale

        sale.paid_amount += instance.amount
        sale.due_amount = sale.total_amount - sale.paid_amount

        if sale.due_amount <= 0:
            sale.status = "PAID"
            sale.due_amount = 0
        elif sale.paid_amount > 0:
            sale.status = "PARTIAL"
        else:
            sale.status = "UNPAID"

        sale.save()

        # CASH IN
        CashbookEntry.objects.create(
            date=instance.date,
            entry_type="IN",
            amount=instance.amount,
            description=f"Payment received for Invoice {sale.invoice_no}"
        )

    # -------------------------
    # 2. PURCHASE PAYMENT
    # -------------------------
    elif instance.type == "PURCHASE" and instance.purchase:

        purchase = instance.purchase

        purchase.paid_amount += instance.amount
        purchase.due_amount = purchase.total_amount - purchase.paid_amount

        if purchase.due_amount <= 0:
            purchase.status = "PAID"
            purchase.due_amount = 0
        elif purchase.paid_amount > 0:
            purchase.status = "PARTIAL"
        else:
            purchase.status = "UNPAID"

        purchase.save()

        # CASH OUT
        CashbookEntry.objects.create(
            date=instance.date,
            entry_type="OUT",
            amount=instance.amount,
            description=f"Payment made for Purchase {purchase.invoice_no}"
        )
        LedgerEntry.objects.create(
            party_type="SUPPLIER",
            party_name=purchase.supplier.name,
            debit=instance.amount,
            credit=0,
            balance=purchase.due_amount,
            description=f"Payment for Purchase {purchase.invoice_no}",
            date=instance.date
        )
