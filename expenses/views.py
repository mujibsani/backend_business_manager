from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Expense
from .serializers import ExpenseSerializer
from .services import create_expense

from .models import ExpenseCategory


class ExpenseViewSet(viewsets.ModelViewSet):

    queryset = Expense.objects.all().order_by("-date", "-id")
    serializer_class = ExpenseSerializer

    def create(self, request, *args, **kwargs):

        category_id = request.data.get("category_id")
        amount = request.data.get("amount")
        date = request.data.get("date")
        description = request.data.get("description", "")

        # -----------------------------
        # VALIDATE CATEGORY
        # -----------------------------
        try:
            category = ExpenseCategory.objects.get(id=category_id)
        except ExpenseCategory.DoesNotExist:
            return Response(
                {"error": "Expense category not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # -----------------------------
        # CREATE EXPENSE
        # -----------------------------
        expense = create_expense(
            category=category,
            amount=amount,
            date=date,
            description=description,
            created_by=request.user,
        )

        serializer = self.get_serializer(expense)

        return Response(
            {
                "message": "Expense created successfully.",
                "expense": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
