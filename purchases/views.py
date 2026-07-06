from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Purchase
from .serializers import PurchaseSerializer
from .services import create_purchase_invoice

from suppliers.models import Supplier


class PurchaseViewSet(viewsets.ModelViewSet):

    queryset = Purchase.objects.all().order_by("-id")
    serializer_class = PurchaseSerializer

    def create(self, request, *args, **kwargs):

        supplier_id = request.data.get("supplier_id")
        invoice_no = request.data.get("invoice_no")
        items = request.data.get("items", [])
        paid_amount = float(request.data.get("paid_amount", 0))
        date = request.data.get("date")

        # -----------------------------
        # VALIDATE ITEMS
        # -----------------------------
        if not items:
            return Response(
                {"error": "Items are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # GET SUPPLIER
        # -----------------------------
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            return Response(
                {"error": "Supplier not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # -----------------------------
        # CREATE PURCHASE (SERVICE LAYER)
        # -----------------------------
        purchase = create_purchase_invoice(
            supplier=supplier,
            invoice_no=invoice_no,
            items=items,
            paid_amount=paid_amount,
            date=date
        )

        serializer = self.get_serializer(purchase)

        return Response(
            {
                "message": "Purchase created successfully",
                "purchase": serializer.data
            },
            status=status.HTTP_201_CREATED
        )