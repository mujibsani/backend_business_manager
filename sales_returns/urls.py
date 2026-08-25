from django.urls import path

from .views import (
    SalesReturnListCreateView,
    SalesReturnDetailView,
)


app_name = "sales_returns"


urlpatterns = [
    # ======================================================
    # LIST + CREATE SALES RETURNS
    # ======================================================

    path(
        "",
        SalesReturnListCreateView.as_view(),
        name="sales-return-list-create",
    ),

    # ======================================================
    # RETRIEVE SALES RETURN
    # ======================================================

    path(
        "<int:pk>/",
        SalesReturnDetailView.as_view(),
        name="sales-return-detail",
    ),
]