from rest_framework import generics

from .models import PurchaseReturn
from .serializers import (
    PurchaseReturnCreateSerializer,
    PurchaseReturnSerializer,
)


# ==========================================================
# LIST + CREATE PURCHASE RETURNS
# ==========================================================

class PurchaseReturnListCreateView(
    generics.ListCreateAPIView
):
    """
    GET:
        List all Purchase Returns.

    POST:
        Create a new Purchase Return.

    Business/accounting logic is handled by:
        purchase_returns.services.create_purchase_return()
    """

    queryset = (
        PurchaseReturn.objects
        .select_related(
            "purchase",
            "supplier",
            "created_by",
        )
        .prefetch_related(
            "items__product",
        )
        .all()
    )

    def get_queryset(self):
        """
        Return Purchase Returns ordered by
        newest date first.
        """

        return (
            self.queryset
            .order_by(
                "-date",
                "-id",
            )
        )

    def get_serializer_class(self):
        """
        Use the write serializer for POST
        and the read serializer for GET.
        """

        if self.request.method == "POST":
            return PurchaseReturnCreateSerializer

        return PurchaseReturnSerializer


# ==========================================================
# RETRIEVE PURCHASE RETURN
# ==========================================================

class PurchaseReturnDetailView(
    generics.RetrieveAPIView
):
    """
    GET:
        Retrieve a single Purchase Return.
    """

    queryset = (
        PurchaseReturn.objects
        .select_related(
            "purchase",
            "supplier",
            "created_by",
        )
        .prefetch_related(
            "items__product",
        )
        .all()
    )

    serializer_class = PurchaseReturnSerializer

    lookup_field = "pk"