from rest_framework import viewsets
from rest_framework.response import Response

from .models import Expense, ExpenseCategory

from .serializers import (
    ExpenseSerializer,
    ExpenseCategorySerializer,
)

from .services import create_expense

from core.permissions import (
    IsAdmin,
    IsAdminOrManager,
    IsStaff,
)


# ==========================================================
# EXPENSE CATEGORY
# ==========================================================

class ExpenseCategoryViewSet(viewsets.ModelViewSet):

    queryset = ExpenseCategory.objects.all().order_by("name")

    serializer_class = ExpenseCategorySerializer

    def get_permissions(self):

        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [IsAdminOrManager()]

        return [IsStaff()]


# ==========================================================
# EXPENSE
# ==========================================================

class ExpenseViewSet(viewsets.ModelViewSet):

    queryset = Expense.objects.select_related(
        "category",
        "created_by",
    ).all().order_by(
        "-date",
        "-id",
    )

    serializer_class = ExpenseSerializer

    def get_permissions(self):

        # Only ADMIN can delete expenses.
        if self.action == "destroy":
            return [IsAdmin()]

        # ADMIN + MANAGER can edit.
        if self.action in [
            "update",
            "partial_update",
        ]:
            return [IsAdminOrManager()]

        # ADMIN + MANAGER + STAFF
        # can view and create.
        return [IsStaff()]

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):

        # ------------------------------------------
        # Validate request
        # ------------------------------------------

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        # ------------------------------------------
        # Create through service
        # ------------------------------------------

        expense = create_expense(
            category=serializer.validated_data["category"],
            amount=serializer.validated_data["amount"],
            date=serializer.validated_data["date"],
            description=serializer.validated_data.get(
                "description",
                "",
            ),
            created_by=request.user,
        )

        # ------------------------------------------
        # Response
        # ------------------------------------------

        response_serializer = self.get_serializer(
            expense
        )

        return Response(
            response_serializer.data,
            status=201,
        )