from django.urls import path

from .views import DashboardAPIView

urlpatterns = [
    path(
        "reports/dashboard/",
        DashboardAPIView.as_view(),
        name="dashboard-report",
    ),
]