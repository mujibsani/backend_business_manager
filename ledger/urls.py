from django.urls import path

from .views import (
    LedgerEntryListAPIView,
    LedgerEntryDetailAPIView,
    CustomerLedgerStatementAPIView,
    SupplierLedgerStatementAPIView,
)

app_name = "ledger"

urlpatterns = [

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

    path(
        "customer/<int:customer_id>/",
        CustomerLedgerStatementAPIView.as_view(),
        name="customer-ledger",
    ),

    path(
        "supplier/<int:supplier_id>/",
        SupplierLedgerStatementAPIView.as_view(),
        name="supplier-ledger",
    ),
]