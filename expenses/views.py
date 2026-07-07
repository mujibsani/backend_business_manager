from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Expense, ExpenseCategory
from .serializers import (
    ExpenseSerializer,
    ExpenseCategorySerializer,
)
from .services import (
    create_expense,
    update_expense,
    delete_expense,
)

from django.db.models import Q
from core.pagination import StandardResultsSetPagination
# ==========================================================
# EXPENSE CATEGORY LIST & CREATE
# ==========================================================

class ExpenseCategoryListCreateAPIView(APIView):

    def get(self, request):

        queryset = ExpenseCategory.objects.filter(
            is_active=True
        ).order_by("name")

        serializer = ExpenseCategorySerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = ExpenseCategorySerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        category = serializer.save()

        return Response(
            ExpenseCategorySerializer(category).data,
            status=status.HTTP_201_CREATED
        )


# ==========================================================
# EXPENSE CATEGORY DETAIL
# ==========================================================

class ExpenseCategoryDetailAPIView(APIView):

    def get(self, request, pk):

        category = get_object_or_404(
            ExpenseCategory,
            pk=pk
        )

        serializer = ExpenseCategorySerializer(category)

        return Response(serializer.data)

    def put(self, request, pk):

        category = get_object_or_404(
            ExpenseCategory,
            pk=pk
        )

        serializer = ExpenseCategorySerializer(
            category,
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):

        category = get_object_or_404(
            ExpenseCategory,
            pk=pk
        )

        category.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================================
# EXPENSE LIST & CREATE
# ==========================================================

class ExpenseListCreateAPIView(APIView):

    def get(self, request):

        queryset = Expense.objects.select_related(
            "category"
        )

        # ==========================================
        # Search
        # ==========================================

        search = request.query_params.get("search")

        if search:

            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )

        # ==========================================
        # Category
        # ==========================================

        category = request.query_params.get("category")

        if category:
            queryset = queryset.filter(
                category_id=category
            )

        # ==========================================
        # Date Range
        # ==========================================

        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        if from_date:
            queryset = queryset.filter(
                date__gte=from_date
            )

        if to_date:
            queryset = queryset.filter(
                date__lte=to_date
            )

        # ==========================================
        # Amount Range
        # ==========================================

        min_amount = request.query_params.get("min_amount")
        max_amount = request.query_params.get("max_amount")

        if min_amount:
            queryset = queryset.filter(
                amount__gte=min_amount
            )

        if max_amount:
            queryset = queryset.filter(
                amount__lte=max_amount
            )

        # ==========================================
        # Ordering
        # ==========================================

        ordering = request.query_params.get("ordering")

        allowed = [
            "date",
            "-date",
            "amount",
            "-amount",
            "id",
            "-id",
        ]

        if ordering in allowed:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-date", "-id")

        paginator = StandardResultsSetPagination()

        page = paginator.paginate_queryset(
            queryset,
            request
        )

        serializer = ExpenseSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )
    

    def post(self, request):

        serializer = ExpenseSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        expense = create_expense(
            category=serializer.validated_data["category"],
            amount=serializer.validated_data["amount"],
            date=serializer.validated_data["date"],
            description=serializer.validated_data.get(
                "description",
                ""
            ),
        )

        return Response(
            ExpenseSerializer(expense).data,
            status=status.HTTP_201_CREATED
        )


# ==========================================================
# EXPENSE DETAIL
# ==========================================================

class ExpenseDetailAPIView(APIView):

    def get(self, request, pk):

        expense = get_object_or_404(
            Expense,
            pk=pk
        )

        serializer = ExpenseSerializer(expense)

        return Response(serializer.data)

    def put(self, request, pk):

        expense = get_object_or_404(
            Expense,
            pk=pk
        )

        serializer = ExpenseSerializer(
            expense,
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        expense = update_expense(
            expense=expense,
            category=serializer.validated_data["category"],
            amount=serializer.validated_data["amount"],
            date=serializer.validated_data["date"],
            description=serializer.validated_data.get(
                "description",
                ""
            ),
        )

        return Response(
            ExpenseSerializer(expense).data
        )

    def delete(self, request, pk):

        expense = get_object_or_404(
            Expense,
            pk=pk
        )

        delete_expense(expense)

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )