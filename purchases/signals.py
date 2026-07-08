from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PurchaseItem
from products.models import Product, StockLog

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import PurchaseItem

@receiver(post_save, sender=PurchaseItem)
def update_purchase_total_on_save(sender, instance, **kwargs):
    instance.purchase.update_totals()


@receiver(post_delete, sender=PurchaseItem)
def update_purchase_total_on_delete(sender, instance, **kwargs):
    instance.purchase.update_totals()