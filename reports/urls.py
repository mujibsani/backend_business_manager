from django.urls import path

from .views import (
    DashboardAPIView,
    SalesReportAPIView,
    PurchaseReportAPIView,
    ExpenseReportAPIView,
    InventoryReportAPIView,
    FinanceReportAPIView,
)


app_name = "reports"


urlpatterns = [

    # Dashboard
    path(
        "dashboard/",
        DashboardAPIView.as_view(),
        name="dashboard",
    ),

    # Sales
    path(
        "sales/",
        SalesReportAPIView.as_view(),
        name="sales-report",
    ),

    # Purchases
    path(
        "purchases/",
        PurchaseReportAPIView.as_view(),
        name="purchase-report",
    ),

    # Expenses
    path(
        "expenses/",
        ExpenseReportAPIView.as_view(),
        name="expense-report",
    ),

    # Inventory
    path(
        "inventory/",
        InventoryReportAPIView.as_view(),
        name="inventory-report",
    ),

    # Finance
    path(
        "finance/",
        FinanceReportAPIView.as_view(),
        name="finance-report",
    ),
]