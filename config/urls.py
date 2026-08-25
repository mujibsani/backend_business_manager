from django.contrib import admin
from django.urls import path, include


urlpatterns = [

    # Django Admin
    path(
        "admin/",
        admin.site.urls,
    ),

    # Reports
    path(
        "api/",
        include("reports.urls"),
    ),

    # Cashbook
    path(
        "api/",
        include("cashbook.urls"),
    ),

    # Ledger
    path(
        "api/",
        include("ledger.urls"),
    ),

    # Payments
    path(
        "api/",
        include("payments.urls"),
    ),

    # Purchase Returns
    path(
        "api/purchase-returns/",
        include("purchase_returns.urls"),
    ),
]