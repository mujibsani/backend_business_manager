from decimal import Decimal

from django.db.models import F, Sum
from django.db.models import DecimalField
from products.models import Product


def get_inventory_summary():

    inventory = Product.objects.aggregate(
        inventory_value=Sum(
            F("stock") * F("cost_price"),
            output_field=DecimalField(),
        )
    )

    return {
        "inventory_value": (
            inventory["inventory_value"]
            or Decimal("0.00")
        ),
        "total_products": Product.objects.count(),
        "low_stock_products": Product.objects.filter(
            stock__lte=F("min_stock")
        ).count(),
    }


def get_low_stock_products():

    return list(
        Product.objects
        .filter(stock__lte=F("min_stock"))
        .values(
            "id",
            "name",
            "stock",
            "min_stock",
        )
        .order_by("stock")
    )


def get_inventory_value():

    result = Product.objects.aggregate(
        total=Sum(
            F("stock") * F("cost_price"),
            output_field=DecimalField(),
        )
    )

    return result["total"] or Decimal("0.00")


