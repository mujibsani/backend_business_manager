from decimal import Decimal

from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import PurchaseReturn, PurchaseReturnItem
from .services import create_purchase_return


# ==========================================================
# CREATE ITEM INPUT
# ==========================================================

class PurchaseReturnItemInputSerializer(serializers.Serializer):
    """
    Input serializer for one Purchase Return item.

    unit_price is intentionally not accepted from the client.
    The service uses the original PurchaseItem.unit_price.
    """

    product_id = serializers.IntegerField(
        required=True
    )

    quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=True,
        min_value=Decimal("0.01"),
    )


# ==========================================================
# CREATE PURCHASE RETURN
# ==========================================================

class PurchaseReturnCreateSerializer(serializers.ModelSerializer):
    """
    Serializer used when creating a Purchase Return.
    """

    items = PurchaseReturnItemInputSerializer(
        many=True,
        required=True,
        allow_empty=False,
    )

    class Meta:
        model = PurchaseReturn

        fields = (
            "purchase",
            "date",
            "items",
            "refund_amount",
            "reason",
        )

        extra_kwargs = {
            "purchase": {
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

        purchase = validated_data.pop("purchase")

        request = self.context.get("request")

        created_by = None

        if request and request.user.is_authenticated:
            created_by = request.user

        try:

            return create_purchase_return(
                purchase=purchase,
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
# PURCHASE RETURN ITEM RESPONSE
# ==========================================================

class PurchaseReturnItemSerializer(
    serializers.ModelSerializer
):
    """
    Read-only representation of a Purchase Return item.
    """

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = PurchaseReturnItem

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
# PURCHASE RETURN RESPONSE
# ==========================================================

class PurchaseReturnSerializer(
    serializers.ModelSerializer
):
    """
    Read-only Purchase Return response serializer.
    """

    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    purchase_invoice_no = serializers.CharField(
        source="purchase.invoice_no",
        read_only=True,
    )

    created_by_name = serializers.SerializerMethodField()

    items = PurchaseReturnItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = PurchaseReturn

        fields = (
            "id",
            "return_no",
            "purchase",
            "purchase_invoice_no",
            "supplier",
            "supplier_name",
            "date",
            "total_amount",
            "refund_amount",
            "status",
            "reason",
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