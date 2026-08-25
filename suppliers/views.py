from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Supplier
from .serializers import SupplierSerializer

from core.permissions import (
    IsStaff,
    IsManager,
    IsAdmin,
)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    Supplier API.

    ADMIN:
        Full access.

    MANAGER:
        View, create and update.

    STAFF:
        View and create.
    """

    queryset = Supplier.objects.all()

    serializer_class = SupplierSerializer

    search_fields = [
        "name",
        "phone",
        "email",
        "division",
        "district",
        "thana",
        "area",
        "address",
    ]

    ordering_fields = [
        "name",
        "created_at",
        "opening_balance",
    ]

    ordering = [
        "name",
    ]

    def get_permissions(self):

        if self.action == "destroy":

            return [
                IsAuthenticated(),
                IsAdmin(),
            ]

        if self.action in (
            "update",
            "partial_update",
        ):

            return [
                IsAuthenticated(),
                IsManager(),
            ]

        return [
            IsAuthenticated(),
            IsStaff(),
        ]