from rest_framework import serializers

from .models import SalesReturn, SalesReturnItem


class SalesReturnItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = SalesReturnItem
        fields = (
            "id",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "subtotal",
        )
        read_only_fields = ("subtotal",)


class SalesReturnSerializer(serializers.ModelSerializer):

    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    sale_invoice = serializers.CharField(
        source="sale.invoice_no",
        read_only=True,
    )

    items = SalesReturnItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = SalesReturn

        fields = (
            "id",
            "return_no",
            "sale",
            "sale_invoice",
            "customer",
            "customer_name",
            "date",
            "total_amount",
            "refund_amount",
            "reason",
            "status",
            "created_by",
            "items",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "total_amount",
            "created_at",
            "updated_at",
        )
