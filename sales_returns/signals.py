
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import SalesReturnItem


@receiver(post_save, sender=SalesReturnItem)
def update_return_total_on_save(sender, instance, **kwargs):
    """
    Recalculate return total whenever an item is added or updated.
    """
    instance.sales_return.update_totals()


@receiver(post_delete, sender=SalesReturnItem)
def update_return_total_on_delete(sender, instance, **kwargs):
    """
    Recalculate return total whenever an item is deleted.
    """
    instance.sales_return.update_totals()
