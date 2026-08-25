from decimal import Decimal, InvalidOperation

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsStaff

from suppliers.models import Supplier

from .models import Purchase
from .serializers import PurchaseSerializer
from .services import create_purchase_invoice


class PurchaseViewSet(viewsets.GenericViewSet):

    queryset = Purchase.objects.all().order_by("-id")
    serializer_class = PurchaseSerializer

    permission_classes = [
        IsAuthenticated,
        IsStaff,
    ]

    # ======================================================
    # LIST
    # ======================================================

    def list(self, request, *args, **kwargs):

        purchases = self.get_queryset()

        serializer = self.get_serializer(
            purchases,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # ======================================================
    # DETAIL
    # ======================================================

    def retrieve(self, request, *args, **kwargs):

        purchase = self.get_object()

        serializer = self.get_serializer(
            purchase,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # ======================================================
    # CREATE
    # ======================================================

    def create(self, request, *args, **kwargs):

        supplier_id = request.data.get("supplier_id")
        invoice_no = request.data.get("invoice_no")
        items = request.data.get("items", [])
        paid_amount = request.data.get("paid_amount", "0")
        date = request.data.get("date")

        # --------------------------------------------------
        # SUPPLIER
        # --------------------------------------------------

        if not supplier_id:
            return Response(
                {
                    "error": "Supplier is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            supplier = Supplier.objects.get(
                pk=supplier_id
            )
        except Supplier.DoesNotExist:
            return Response(
                {
                    "error": "Supplier not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # --------------------------------------------------
        # INVOICE NUMBER
        # --------------------------------------------------

        if not invoice_no:
            return Response(
                {
                    "error": "Invoice number is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # ITEMS
        # --------------------------------------------------

        if not isinstance(items, list) or not items:
            return Response(
                {
                    "error": "Items are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # PAID AMOUNT
        # --------------------------------------------------

        try:
            paid_amount = Decimal(
                str(paid_amount)
            )
        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ):
            return Response(
                {
                    "error": "Invalid paid amount."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if paid_amount < 0:
            return Response(
                {
                    "error": (
                        "Paid amount cannot "
                        "be negative."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # CREATE PURCHASE
        # --------------------------------------------------

        try:

            purchase = create_purchase_invoice(
                supplier=supplier,
                invoice_no=invoice_no,
                items=items,
                paid_amount=paid_amount,
                date=date,
            )

        except Exception as exc:

            return Response(
                {
                    "error": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        serializer = self.get_serializer(
            purchase
        )

        return Response(
            {
                "message": (
                    "Purchase created successfully."
                ),
                "purchase": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )