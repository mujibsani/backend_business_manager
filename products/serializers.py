from rest_framework import serializers

from .models import Category, Product, StockLog


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = (
            "id",
            "name",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = Product

        fields = (
            "id",
            "name",
            "category",
            "category_name",
            "cost_price",
            "selling_price",
            "stock",
            "min_stock",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "stock",
            "created_at",
            "updated_at",
        )

    def validate_cost_price(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Cost price cannot be negative."
            )

        return value

    def validate_selling_price(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Selling price cannot be negative."
            )

        return value

    def validate_min_stock(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "Minimum stock cannot be negative."
            )

        return value


class StockLogSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = StockLog

        fields = (
            "id",
            "product",
            "product_name",
            "quantity",
            "type",
            "reference",
            "created_at",
        )

        read_only_fields = (
            "id",
            "product",
            "quantity",
            "type",
            "reference",
            "created_at",
        )