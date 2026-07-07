from django.urls import path

from .views import (
    ExpenseCategoryListCreateAPIView,
    ExpenseCategoryDetailAPIView,
    ExpenseListCreateAPIView,
    ExpenseDetailAPIView,
)

urlpatterns = [

    # ==========================================
    # Expense Categories
    # ==========================================

    path(
        "categories/",
        ExpenseCategoryListCreateAPIView.as_view(),
        name="expense-category-list",
    ),

    path(
        "categories/<int:pk>/",
        ExpenseCategoryDetailAPIView.as_view(),
        name="expense-category-detail",
    ),

    # ==========================================
    # Expenses
    # ==========================================

    path(
        "",
        ExpenseListCreateAPIView.as_view(),
        name="expense-list",
    ),

    path(
        "<int:pk>/",
        ExpenseDetailAPIView.as_view(),
        name="expense-detail",
    ),

]