from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("reports.urls")),
    path("api/", include("cashbook.urls")),
    path("api/", include("ledger.urls")),
    path("api/", include("payments.urls")),
]
