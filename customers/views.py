from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Customer
from .serializers import CustomerSerializer

from core.permissions import (
    IsStaff,
    IsManager,
    IsAdmin,
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    Customer API.

    Roles:

    ADMIN
        Full access.

    MANAGER
        View, create and update.

    STAFF
        View and create only.
    """

    queryset = Customer.objects.select_related(
        "division",
        "district",
        "thana",
    ).all()

    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsStaff]

    search_fields = [
        "name",
        "phone",
        "email",
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

        if self.action in [
            "update",
            "partial_update",
        ]:

            return [
                IsAuthenticated(),
                IsManager(),
            ]

        return [
            IsAuthenticated(),
            IsStaff(),
        ]