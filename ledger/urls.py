from django.urls import path

from .views import (
    LedgerEntryListAPIView,
    LedgerEntryDetailAPIView,
    CustomerLedgerStatementAPIView,
    SupplierLedgerStatementAPIView,
)

app_name = "ledger"

urlpatterns = [

    # ==========================================================
    # Ledger Entries
    # ==========================================================

    path(
        "",
        LedgerEntryListAPIView.as_view(),
        name="ledger-list",
    ),

    path(
        "<int:pk>/",
        LedgerEntryDetailAPIView.as_view(),
        name="ledger-detail",
    ),

    # ==========================================================
    # Customer Ledger Statement
    # ==========================================================

    path(
        "customer/<int:customer_id>/",
        CustomerLedgerStatementAPIView.as_view(),
        name="customer-ledger",
    ),

    # ==========================================================
    # Supplier Ledger Statement
    # ==========================================================

    path(
        "supplier/<int:supplier_id>/",
        SupplierLedgerStatementAPIView.as_view(),
        name="supplier-ledger",
    ),

]