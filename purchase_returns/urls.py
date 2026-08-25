from django.urls import path

from .views import (
    PurchaseReturnListCreateView,
    PurchaseReturnDetailView,
)


app_name = "purchase_returns"


urlpatterns = [
    path(
        "",
        PurchaseReturnListCreateView.as_view(),
        name="purchase-return-list-create",
    ),

    path(
        "<int:pk>/",
        PurchaseReturnDetailView.as_view(),
        name="purchase-return-detail",
    ),
]