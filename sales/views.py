from django.core.exceptions import ValidationError
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsStaff
from customers.models import Customer

from .models import Sale
from .serializers import SaleSerializer
from .services import create_sale_invoice


# ==========================================================
# CREATE SALE
# ==========================================================

@api_view(["POST"])
@permission_classes([IsStaff])
def create_sale(request):
    """
    Create a sale invoice.

    ADMIN:
        Allowed

    MANAGER:
        Allowed

    STAFF:
        Allowed
    """

    data = request.data

    customer_id = data.get("customer_id")
    items = data.get("items", [])
    paid_amount = data.get(
        "paid_amount",
        "0.00",
    )

    date = data.get(
        "date",
        timezone.localdate(),
    )

    # ------------------------------------------------------
    # CUSTOMER
    # ------------------------------------------------------

    if not customer_id:

        return Response(
            {
                "error": "customer_id is required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        customer = Customer.objects.get(
            pk=customer_id
        )

    except Customer.DoesNotExist:

        return Response(
            {
                "error": "Customer not found."
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # ------------------------------------------------------
    # ITEMS
    # ------------------------------------------------------

    if not isinstance(items, list) or not items:

        return Response(
            {
                "error": (
                    "At least one sale item is required."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # INVOICE NUMBER
    # ------------------------------------------------------

    invoice_no = (
        "SALE-"
        f"{timezone.now().strftime('%Y%m%d%H%M%S%f')}"
    )

    # ------------------------------------------------------
    # CREATE SALE
    # ------------------------------------------------------

    try:

        sale = create_sale_invoice(
            customer=customer,
            invoice_no=invoice_no,
            items=items,
            paid_amount=paid_amount,
            date=date,
            sales_person=request.user,
        )

    except ValidationError as exc:

        return Response(
            {
                "error": str(exc)
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except (TypeError, ValueError):

        return Response(
            {
                "error": (
                    "Invalid numeric value provided."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = SaleSerializer(sale)

    return Response(
        {
            "message": "Sale created successfully.",
            "sale": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )


# ==========================================================
# SALE LIST
# ==========================================================

class SaleListView(APIView):
    """
    List sale invoices.

    ADMIN:
        Allowed

    MANAGER:
        Allowed

    STAFF:
        Allowed
    """

    permission_classes = [IsStaff]

    def get(self, request):

        queryset = (
            Sale.objects
            .select_related(
                "customer",
                "sales_person",
            )
            .prefetch_related(
                "items__product",
            )
            .order_by("-date", "-id")
        )

        # --------------------------------------------------
        # SEARCH
        # --------------------------------------------------

        search = request.query_params.get(
            "search"
        )

        if search:

            queryset = queryset.filter(
                invoice_no__icontains=search
            )

        # --------------------------------------------------
        # CUSTOMER FILTER
        # --------------------------------------------------

        customer_id = request.query_params.get(
            "customer_id"
        )

        if customer_id:

            queryset = queryset.filter(
                customer_id=customer_id
            )

        # --------------------------------------------------
        # STATUS FILTER
        # --------------------------------------------------

        sale_status = request.query_params.get(
            "status"
        )

        if sale_status in dict(
            Sale.STATUS_CHOICES
        ):

            queryset = queryset.filter(
                status=sale_status
            )

        # --------------------------------------------------
        # DATE FILTER
        # --------------------------------------------------

        date = request.query_params.get(
            "date"
        )

        if date:

            queryset = queryset.filter(
                date=date
            )

        serializer = SaleSerializer(
            queryset,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# SALE DETAIL
# ==========================================================

class SaleDetailView(APIView):
    """
    Retrieve a single sale invoice.

    ADMIN:
        Allowed

    MANAGER:
        Allowed

    STAFF:
        Allowed
    """

    permission_classes = [IsStaff]

    def get(self, request, pk):

        try:

            sale = (
                Sale.objects
                .select_related(
                    "customer",
                    "sales_person",
                )
                .prefetch_related(
                    "items__product",
                )
                .get(pk=pk)
            )

        except Sale.DoesNotExist:

            return Response(
                {
                    "error": "Sale not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SaleSerializer(sale)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )