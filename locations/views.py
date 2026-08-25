from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Division, District, Thana

from .serializers import (
    DivisionSerializer,
    DistrictSerializer,
    ThanaSerializer,
)

from core.permissions import (
    IsAdmin,
    IsStaff,
)


class DivisionViewSet(viewsets.ModelViewSet):

    queryset = Division.objects.all().order_by("name")
    serializer_class = DivisionSerializer

    search_fields = [
        "name",
    ]

    def get_permissions(self):

        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [
                IsAuthenticated(),
                IsAdmin(),
            ]

        return [
            IsAuthenticated(),
            IsStaff(),
        ]


class DistrictViewSet(viewsets.ModelViewSet):

    queryset = District.objects.select_related(
        "division"
    ).all().order_by("name")

    serializer_class = DistrictSerializer

    # search_fields = [
    #     "name",
    #     "division__name",
    # ]

    # filterset_fields = [
    #     "division",
    # ]

    def get_permissions(self):

        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [
                IsAuthenticated(),
                IsAdmin(),
            ]

        return [
            IsAuthenticated(),
            IsStaff(),
        ]


class ThanaViewSet(viewsets.ModelViewSet):

    queryset = Thana.objects.select_related(
        "district",
        "district__division",
    ).all().order_by("name")

    serializer_class = ThanaSerializer

    search_fields = [
        "name",
        "district__name",
        "district__division__name",
    ]

    # filterset_fields = [
    #     "district",
    # ]

    def get_permissions(self):

        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [
                IsAuthenticated(),
                IsAdmin(),
            ]

        return [
            IsAuthenticated(),
            IsStaff(),
        ]