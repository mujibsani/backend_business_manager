from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsStaff

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
    Purchase Return API.

    GET:
        List purchase returns.

    POST:
        Create a purchase return.

    Roles:
        ADMIN
        MANAGER
        STAFF
    """

    permission_classes = [
        IsAuthenticated,
        IsStaff,
    ]

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

    # ======================================================
    # QUERYSET
    # ======================================================

    def get_queryset(self):

        return (
            self.queryset
            .order_by(
                "-date",
                "-id",
            )
        )

    # ======================================================
    # SERIALIZER
    # ======================================================

    def get_serializer_class(self):

        if self.request.method == "POST":
            return PurchaseReturnCreateSerializer

        return PurchaseReturnSerializer


# ==========================================================
# PURCHASE RETURN DETAIL
# ==========================================================

class PurchaseReturnDetailView(
    generics.RetrieveAPIView
):
    """
    Retrieve a single Purchase Return.

    Roles:
        ADMIN
        MANAGER
        STAFF
    """

    permission_classes = [
        IsAuthenticated,
        IsStaff,
    ]

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