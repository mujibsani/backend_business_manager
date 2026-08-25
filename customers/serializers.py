from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "division",
            "district",
            "thana",
            "area",
            "address",
            "opening_balance",
            "opening_balance_type",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_phone(self, value):
        """
        Prevent duplicate phone numbers.

        During update, allow the customer's own
        existing phone number.
        """

        queryset = Customer.objects.filter(phone=value)

        instance = self.instance

        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "This phone number already exists."
            )

        return value

    def validate_opening_balance(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Opening balance cannot be negative."
            )

        return value