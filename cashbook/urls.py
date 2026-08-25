from django.urls import path

from .views import CashbookAPIView


urlpatterns = [
    path(
        "",
        CashbookAPIView.as_view(),
        name="cashbook",
    ),
]