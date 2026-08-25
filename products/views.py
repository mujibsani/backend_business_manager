from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import (
    IsAdmin,
    IsAdminOrManager,
    IsStaff,
)

from .models import Category, Product, StockLog
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    StockLogSerializer,
)
from .services import stock_in as increase_stock
from .services import stock_out as decrease_stock


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Category API.

    ADMIN:
        Full access.

    MANAGER:
        List, retrieve, create and update.

    STAFF:
        List and retrieve only.
    """

    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    def get_permissions(self):

        if self.action in ["list", "retrieve"]:
            permission_classes = [IsStaff]

        elif self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            permission_classes = [IsAdminOrManager]

        elif self.action == "destroy":
            permission_classes = [IsAdmin]

        else:
            permission_classes = [IsAuthenticated]

        return [
            permission()
            for permission in permission_classes
        ]


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product API.

    ADMIN:
        Full access.

    MANAGER:
        List, retrieve, create and update.

    STAFF:
        List and retrieve only.

    Stock is intentionally read-only through normal
    product create/update operations.
    """

    queryset = (
        Product.objects
        .select_related("category")
        .all()
        .order_by("name")
    )

    serializer_class = ProductSerializer

    def get_permissions(self):

        if self.action in ["list", "retrieve"]:
            permission_classes = [IsStaff]

        elif self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            permission_classes = [IsAdminOrManager]

        elif self.action == "destroy":
            permission_classes = [IsAdmin]

        elif self.action in [
            "stock_in",
            "stock_out",
        ]:
            permission_classes = [IsAdminOrManager]

        else:
            permission_classes = [IsAuthenticated]

        return [
            permission()
            for permission in permission_classes
        ]

    @action(
        detail=True,
        methods=["post"],
        url_path="stock-in",
    )
    def stock_in(self, request, pk=None):
        """
        Increase product stock.
        """

        product = self.get_object()

        quantity = request.data.get("quantity")
        reference = request.data.get("reference")

        if quantity is None:
            return Response(
                {
                    "detail": "Quantity is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not reference:
            return Response(
                {
                    "detail": "Reference is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            increase_stock(
                product=product,
                quantity=quantity,
                reference=reference,
            )

        except Exception as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        product.refresh_from_db()

        serializer = self.get_serializer(product)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="stock-out",
    )
    def stock_out(self, request, pk=None):
        """
        Reduce product stock.
        """

        product = self.get_object()

        quantity = request.data.get("quantity")
        reference = request.data.get("reference")

        if quantity is None:
            return Response(
                {
                    "detail": "Quantity is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not reference:
            return Response(
                {
                    "detail": "Reference is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            decrease_stock(
                product=product,
                quantity=quantity,
                reference=reference,
            )

        except Exception as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        product.refresh_from_db()

        serializer = self.get_serializer(product)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class StockLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Stock history API.

    ADMIN:
        View.

    MANAGER:
        View.

    STAFF:
        View.

    Stock logs cannot be manually created,
    modified or deleted.
    """

    queryset = (
        StockLog.objects
        .select_related("product")
        .all()
        .order_by("-created_at")
    )

    serializer_class = StockLogSerializer
    permission_classes = [IsStaff]