from rest_framework import serializers

from .models import Expense, ExpenseCategory


# ==========================================================
# Expense Category
# ==========================================================

class ExpenseCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenseCategory
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]


# ==========================================================
# Expense
# ==========================================================

class ExpenseSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = Expense

        fields = [
            "id",
            "category",
            "category_name",
            "amount",
            "date",
            "description",
            "created_at",
            "updated_at",
        ]

    def validate_amount(self, value):

        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than zero."
            )

        return value

    def validate(self, attrs):

        category = attrs.get("category")

        if category and not category.is_active:
            raise serializers.ValidationError({
                "category": "Selected category is inactive."
            })

        return attrs