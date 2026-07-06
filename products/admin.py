from django.contrib import admin
from .models import Product, Category, StockLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "category",
        "stock",
        "min_stock",
        "selling_price",
        "cost_price"
    )

    list_filter = ("category",)
    search_fields = ("name",)

    readonly_fields = ("stock",)


@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "product",
        "quantity",
        "type",
        "reference",
        "created_at"
    )

    list_filter = ("type", "product")
    readonly_fields = ("product", "quantity", "type", "reference", "created_at")

    def has_add_permission(self, request):
        return False
    

