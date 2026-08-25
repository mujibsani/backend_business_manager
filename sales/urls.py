from django.urls import path

from .views import (
    SaleDetailView,
    SaleListView,
    create_sale,
)


app_name = "sales"


urlpatterns = [

    # Create Sale
    path(
        "create/",
        create_sale,
        name="create-sale",
    ),

    # List Sales
    path(
        "",
        SaleListView.as_view(),
        name="sale-list",
    ),

    # Sale Detail
    path(
        "<int:pk>/",
        SaleDetailView.as_view(),
        name="sale-detail",
    ),

]