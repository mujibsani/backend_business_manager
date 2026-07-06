from django.urls import path
from .views import CashbookAPIView

urlpatterns = [
    path("cashbook/", CashbookAPIView.as_view()),
]