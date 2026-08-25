from rest_framework import serializers

from .models import Purchase, PurchaseItem


# ==========================================================
# PURCHASE ITEM
# ==========================================================

class PurchaseItemSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = PurchaseItem
        fields = "__all__"


# ==========================================================
# PURCHASE
# ==========================================================

class PurchaseSerializer(
    serializers.ModelSerializer
):

    items = PurchaseItemSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Purchase
        fields = "__all__"
