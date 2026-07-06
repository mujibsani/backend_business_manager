from django.utils import timezone
from django.db import transaction

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from customers.models import Customer
from products.models import Product

from .models import Sale, SaleItem
from .serializers import SaleSerializer
from .services import process_sale_accounting


# -----------------------------
# CREATE SALE INVOICE API
# -----------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_sale(request):

    data = request.data

    customer_id = data.get("customer_id")
    items = data.get("items", [])
    paid_amount = float(data.get("paid_amount", 0))
    date = data.get("date", timezone.now().date())

    if not items:
        return Response({"error": "Items are required"}, status=400)

    # -----------------------------
    # GET CUSTOMER
    # -----------------------------
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=404)

    # -----------------------------
    # CREATE INVOICE NO
    # -----------------------------
    invoice_no = f"SALE-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    # -----------------------------
    # CREATE SALE
    # -----------------------------
    sale = Sale.objects.create(
        invoice_no=invoice_no,
        customer=customer,
        sales_person=request.user,
        date=date,
        paid_amount=paid_amount,
    )

    total = 0

    # -----------------------------
    # CREATE ITEMS + STOCK UPDATE
    # -----------------------------
    for item in items:

        product_id = item.get("product_id")
        quantity = float(item.get("quantity", 0))
        unit_price = float(item.get("unit_price", 0))

        if quantity <= 0:
            continue

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": f"Product {product_id} not found"},
                status=404
            )

        # STOCK CHECK
        if product.stock < quantity:
            return Response(
                {"error": f"Not enough stock for {product.name}"},
                status=400
            )

        # CREATE ITEM
        sale_item = SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
        )

        total += float(sale_item.subtotal)

        # REDUCE STOCK
        product.stock -= quantity
        product.save()

    # -----------------------------
    # UPDATE SALE TOTALS
    # -----------------------------
    sale.total_amount = total
    sale.due_amount = total - sale.paid_amount

    if sale.due_amount <= 0:
        sale.status = "PAID"
        sale.due_amount = 0
    elif sale.paid_amount > 0:
        sale.status = "PARTIAL"
    else:
        sale.status = "UNPAID"

    sale.save()

    # -----------------------------
    # ACCOUNTING (CASHBOOK + LEDGER)
    # -----------------------------
    process_sale_accounting(sale, customer)

    serializer = SaleSerializer(sale)

    return Response({
        "message": "Sale created successfully",
        "sale": serializer.data
    })