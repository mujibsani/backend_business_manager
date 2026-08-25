from rest_framework import serializers

from .models import Payment


class PaymentSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Payment

        fields = "__all__"

        read_only_fields = (
            "payment_no",
            "received_by",
        )

    def validate(self, attrs):

        payment_type = attrs.get(
            "payment_type"
        )

        sale = attrs.get(
            "sale"
        )

        purchase = attrs.get(
            "purchase"
        )

        customer = attrs.get(
            "customer"
        )

        supplier = attrs.get(
            "supplier"
        )

        amount = attrs.get(
            "amount"
        )

        # ==================================================
        # AMOUNT
        # ==================================================

        if amount is None:

            raise serializers.ValidationError(
                {
                    "amount": (
                        "Amount is required."
                    )
                }
            )

        if amount <= 0:

            raise serializers.ValidationError(
                {
                    "amount": (
                        "Amount must be greater "
                        "than zero."
                    )
                }
            )

        # ==================================================
        # CUSTOMER PAYMENT
        # ==================================================

        if payment_type == "CUSTOMER":

            # Customer OR sale must exist.
            if not customer and not sale:

                raise serializers.ValidationError(
                    {
                        "customer": (
                            "Customer or Sale is "
                            "required for customer "
                            "payment."
                        )
                    }
                )

            # Supplier must never be present.
            if supplier:

                raise serializers.ValidationError(
                    {
                        "supplier": (
                            "Supplier must be empty "
                            "for customer payment."
                        )
                    }
                )

            # Sale must belong to customer.
            if (
                sale
                and customer
                and sale.customer_id
                != customer.id
            ):

                raise serializers.ValidationError(
                    {
                        "sale": (
                            "Selected sale does not "
                            "belong to selected customer."
                        )
                    }
                )

            # Payment against sale.
            if sale:

                if amount > sale.due_amount:

                    raise serializers.ValidationError(
                        {
                            "amount": (
                                "Payment exceeds "
                                "the sale due amount."
                            )
                        }
                    )

        # ==================================================
        # SUPPLIER PAYMENT
        # ==================================================

        elif payment_type == "SUPPLIER":

            # Supplier OR purchase must exist.
            if not supplier and not purchase:

                raise serializers.ValidationError(
                    {
                        "supplier": (
                            "Supplier or Purchase is "
                            "required for supplier "
                            "payment."
                        )
                    }
                )

            # Customer must never be present.
            if customer:

                raise serializers.ValidationError(
                    {
                        "customer": (
                            "Customer must be empty "
                            "for supplier payment."
                        )
                    }
                )

            # Purchase must belong to supplier.
            if (
                purchase
                and supplier
                and purchase.supplier_id
                != supplier.id
            ):

                raise serializers.ValidationError(
                    {
                        "purchase": (
                            "Selected purchase does not "
                            "belong to selected supplier."
                        )
                    }
                )

            # Payment against purchase.
            if purchase:

                if amount > purchase.due_amount:

                    raise serializers.ValidationError(
                        {
                            "amount": (
                                "Payment exceeds "
                                "the purchase due amount."
                            )
                        }
                    )

        else:

            raise serializers.ValidationError(
                {
                    "payment_type": (
                        "Payment type must be "
                        "CUSTOMER or SUPPLIER."
                    )
                }
            )

        return attrs
