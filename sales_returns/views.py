from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsStaff

from .models import SalesReturn

from .serializers import (
    SalesReturnCreateSerializer,
    SalesReturnSerializer,
)


# ==========================================================
# LIST + CREATE SALES RETURNS
# ==========================================================

class SalesReturnListCreateView(
    generics.ListCreateAPIView
):

    queryset = (
        SalesReturn.objects
        .select_related(
            "sale",
            "customer",
            "created_by",
        )
        .prefetch_related(
            "items__product",
        )
        .all()
    )

    # ------------------------------------------------------
    # ROLE BASED PERMISSION
    # ------------------------------------------------------

    def get_permissions(self):

        # ADMIN + MANAGER + STAFF
        #
        # All three roles can:
        #     GET  /api/sales-returns/
        #     POST /api/sales-returns/
        #
        # IsStaff represents the three business roles.
        return [
            IsAuthenticated(),
            IsStaff(),
        ]

    # ------------------------------------------------------
    # QUERYSET
    # ------------------------------------------------------

    def get_queryset(self):

        return (
            self.queryset
            .order_by(
                "-date",
                "-id",
            )
        )

    # ------------------------------------------------------
    # SERIALIZER
    # ------------------------------------------------------

    def get_serializer_class(self):

        if self.request.method == "POST":

            return SalesReturnCreateSerializer

        return SalesReturnSerializer

    # ------------------------------------------------------
    # CREATE
    # ------------------------------------------------------

    def perform_create(self, serializer):

        serializer.save(
            created_by=self.request.user
        )


# ==========================================================
# DETAIL
# ==========================================================

class SalesReturnDetailView(
    generics.RetrieveAPIView
):

    queryset = (
        SalesReturn.objects
        .select_related(
            "sale",
            "customer",
            "created_by",
        )
        .prefetch_related(
            "items__product",
        )
        .all()
    )

    serializer_class = SalesReturnSerializer

    lookup_field = "pk"

    permission_classes = [
        IsAuthenticated,
        IsStaff,
    ]
