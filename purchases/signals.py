from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PurchaseItem
from products.models import Product, StockLog

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import PurchaseItem

@receiver(post_save, sender=PurchaseItem)
def update_stock_on_purchase(sender, instance, created, **kwargs):

    if not created:
        return

    product = instance.product

    # increase stock
    product.stock += instance.quantity
    product.save()

    # log
    StockLog.objects.create(
        product=product,
        quantity=instance.quantity,
        type="IN",
        reference=f"PURCHASE-{instance.purchase.invoice_no}"
    )





@receiver(post_save, sender=PurchaseItem)
def update_purchase_total_on_save(sender, instance, **kwargs):
    instance.purchase.update_totals()


@receiver(post_delete, sender=PurchaseItem)
def update_purchase_total_on_delete(sender, instance, **kwargs):
    instance.purchase.update_totals()