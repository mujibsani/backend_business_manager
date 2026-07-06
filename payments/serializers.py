from rest_framework import serializers

from .models import Payment
from sales.models import Sale
from purchases.models import Purchase
from customers.models import Customer
from suppliers.models import Supplier


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("payment_no",)

    def validate(self, attrs):

        payment_type = attrs.get("payment_type")
        sale = attrs.get("sale")
        purchase = attrs.get("purchase")
        customer = attrs.get("customer")
        supplier = attrs.get("supplier")
        amount = attrs.get("amount")

        if amount and amount <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")

        # -----------------------------
        # CUSTOMER VALIDATION
        # -----------------------------
        if payment_type == "CUSTOMER":

            if not customer and not sale:
                raise serializers.ValidationError(
                    "Customer or Sale is required for customer payment."
                )

            if sale and customer and sale.customer != customer:
                raise serializers.ValidationError(
                    "Sale does not belong to selected customer."
                )

            if sale:
                if sale.due_amount < amount:
                    raise serializers.ValidationError(
                        "Payment exceeds due amount."
                    )

        # -----------------------------
        # SUPPLIER VALIDATION
        # -----------------------------
        elif payment_type == "SUPPLIER":

            if not supplier and not purchase:
                raise serializers.ValidationError(
                    "Supplier or Purchase is required for supplier payment."
                )

            if purchase and supplier and purchase.supplier != supplier:
                raise serializers.ValidationError(
                    "Purchase does not belong to selected supplier."
                )

            if purchase:
                if purchase.due_amount < amount:
                    raise serializers.ValidationError(
                        "Payment exceeds due amount."
                    )

        return attrs