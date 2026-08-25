from django.urls import path

from .views import (
    PurchaseReturnListCreateView,
    PurchaseReturnDetailView,
)


app_name = "purchase_returns"


urlpatterns = [

    # ======================================================
    # LIST + CREATE
    # ======================================================

    path(
        "",
        PurchaseReturnListCreateView.as_view(),
        name="purchase-return-list-create",
    ),

    # ======================================================
    # DETAIL
    # ======================================================

    path(
        "<int:pk>/",
        PurchaseReturnDetailView.as_view(),
        name="purchase-return-detail",
    ),
]