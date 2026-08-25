from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductViewSet,
    StockLogViewSet,
)

router = DefaultRouter()

router.register(
    r"categories",
    CategoryViewSet,
    basename="category",
)

router.register(
    r"products",
    ProductViewSet,
    basename="product",
)

router.register(
    r"stock-logs",
    StockLogViewSet,
    basename="stock-log",
)

urlpatterns = router.urls