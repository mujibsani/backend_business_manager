from decimal import Decimal

from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import (
    SalesReturn,
    SalesReturnItem,
)
from .services import create_sales_return


# ==========================================================
# CREATE ITEM INPUT
# ==========================================================

class SalesReturnItemInputSerializer(
    serializers.Serializer
):

    product_id = serializers.IntegerField(
        required=True,
    )

    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=True,
        min_value=Decimal("0.01"),
    )


# ==========================================================
# CREATE SALES RETURN
# ==========================================================

class SalesReturnCreateSerializer(
    serializers.ModelSerializer
):

    items = SalesReturnItemInputSerializer(
        many=True,
        required=True,
        allow_empty=False,
    )

    class Meta:
        model = SalesReturn

        fields = (
            "sale",
            "date",
            "items",
            "refund_amount",
            "reason",
        )

        extra_kwargs = {
            "sale": {
                "required": True,
            },
            "date": {
                "required": False,
            },
            "refund_amount": {
                "required": False,
                "default": Decimal("0.00"),
                "min_value": Decimal("0.00"),
            },
            "reason": {
                "required": False,
                "allow_blank": True,
            },
        }

    def validate_refund_amount(self, value):

        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "Refund amount cannot be negative."
            )

        return value

    def create(self, validated_data):

        items = validated_data.pop("items")

        sale = validated_data.pop("sale")

        request = self.context.get("request")

        created_by = None

        if request and request.user.is_authenticated:
            created_by = request.user

        try:

            return create_sales_return(
                sale=sale,
                items=items,
                refund_amount=validated_data.get(
                    "refund_amount",
                    Decimal("0.00"),
                ),
                reason=validated_data.get(
                    "reason",
                    "",
                ),
                created_by=created_by,
                date=validated_data.get("date"),
            )

        except ValidationError as exc:

            if hasattr(exc, "messages"):
                message = exc.messages
            else:
                message = str(exc)

            raise serializers.ValidationError(
                message
            )


# ==========================================================
# RETURN ITEM RESPONSE
# ==========================================================

class SalesReturnItemSerializer(
    serializers.ModelSerializer
):

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

        read_only_fields = fields


# ==========================================================
# RETURN RESPONSE
# ==========================================================

class SalesReturnSerializer(
    serializers.ModelSerializer
):

    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    sale_invoice = serializers.CharField(
        source="sale.invoice_no",
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()

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
            "created_by_name",
            "items",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_created_by_name(self, obj):

        if not obj.created_by:
            return None

        full_name = obj.created_by.get_full_name()

        if full_name:
            return full_name

        return obj.created_by.username