from django.urls import path

from .views import PurchaseViewSet


app_name = "purchases"


urlpatterns = [

    # ======================================================
    # PURCHASE LIST + CREATE
    # ======================================================

    path(
        "",
        PurchaseViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="purchase-list",
    ),

    # ======================================================
    # PURCHASE DETAIL
    # ======================================================

    path(
        "<int:pk>/",
        PurchaseViewSet.as_view(
            {
                "get": "retrieve",
            }
        ),
        name="purchase-detail",
    ),
]
