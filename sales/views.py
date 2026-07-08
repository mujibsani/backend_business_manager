from django.utils import timezone
from django.db import transaction

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from customers.models import Customer

from .serializers import SaleSerializer
from .services import create_sale_invoice


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_sale(request):

    data = request.data

    customer_id = data.get("customer_id")
    items = data.get("items", [])
    paid_amount = data.get("paid_amount", 0)
    date = data.get("date", timezone.now().date())

    if not items:
        return Response(
            {"error": "Items are required"},
            status=400,
        )

    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist:
        return Response(
            {"error": "Customer not found"},
            status=404,
        )

    invoice_no = f"SALE-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    sale = create_sale_invoice(
        customer=customer,
        invoice_no=invoice_no,
        items=items,
        paid_amount=paid_amount,
        date=date,
        sales_person=request.user,
    )

    serializer = SaleSerializer(sale)

    return Response(
        {
            "message": "Sale created successfully",
            "sale": serializer.data,
        },
        status=201,
    )