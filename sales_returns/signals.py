from django.db.models.signals import (
    post_save,
    post_delete,
)

from django.dispatch import receiver

from .models import SalesReturnItem


@receiver(
    post_save,
    sender=SalesReturnItem,
)
def update_return_total_on_save(
    sender,
    instance,
    **kwargs,
):

    instance.sales_return.update_totals()


@receiver(
    post_delete,
    sender=SalesReturnItem,
)
def update_return_total_on_delete(
    sender,
    instance,
    **kwargs,
):

    instance.sales_return.update_totals()