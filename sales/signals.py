from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Sale, SaleItem
from products.models import StockLog, Product


@receiver(post_save, sender=SaleItem)
def update_stock_on_sale(sender, instance, created, **kwargs):

    if not created:
        return

    product = instance.product

    # decrease stock
    product.stock -= instance.quantity
    product.save()

    # log
    StockLog.objects.create(
        product=product,
        quantity=instance.quantity,
        type="OUT",
        reference=f"SALE-{instance.sale.invoice_no}"
    )

@receiver(post_save, sender=SaleItem)
def update_sale_total(sender, instance, created, **kwargs):

    if not created:
        return

    sale = instance.sale
    sale.update_totals()