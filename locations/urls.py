from rest_framework.routers import DefaultRouter

from .views import (
    DivisionViewSet,
    DistrictViewSet,
    ThanaViewSet,
)


router = DefaultRouter()

router.register(
    "divisions",
    DivisionViewSet,
    basename="division",
)

router.register(
    "districts",
    DistrictViewSet,
    basename="district",
)

router.register(
    "thanas",
    ThanaViewSet,
    basename="thana",
)


urlpatterns = router.urls