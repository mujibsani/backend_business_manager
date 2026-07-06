from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer

from .services import (
    receive_customer_payment,
    receive_customer_advance,
    pay_supplier,
    supplier_advance_payment
)

from sales.models import Sale
from purchases.models import Purchase
from customers.models import Customer
from suppliers.models import Supplier


class PaymentViewSet(viewsets.ModelViewSet):

    queryset = Payment.objects.all().order_by("-id")
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):

        data = request.data
        payment_type = data.get("payment_type")
        amount = data.get("amount")
        payment_date = data.get("payment_date")
        payment_method = data.get("payment_method", "CASH")
        reference_no = data.get("reference_no", "")
        note = data.get("note", "")
        transaction_id = data.get("transaction_id", "")

        sale_id = data.get("sale")
        purchase_id = data.get("purchase")
        customer_id = data.get("customer")
        supplier_id = data.get("supplier")

        payment = None

        # -----------------------------
        # CUSTOMER
        # -----------------------------
        if payment_type == "CUSTOMER":

            if sale_id:
                sale = Sale.objects.get(id=sale_id)
                payment = receive_customer_payment(
                    sale=sale,
                    amount=amount,
                    payment_date=payment_date,
                    payment_method=payment_method,
                    received_by=request.user,
                    transaction_id=transaction_id,
                    reference_no=reference_no,
                    note=note,
                )

            else:
                customer = Customer.objects.get(id=customer_id)
                payment = receive_customer_advance(
                    customer=customer,
                    amount=amount,
                    payment_date=payment_date,
                    payment_method=payment_method,
                    received_by=request.user,
                    transaction_id=transaction_id,
                    reference_no=reference_no,
                    note=note,
                )

        # -----------------------------
        # SUPPLIER
        # -----------------------------
        elif payment_type == "SUPPLIER":

            if purchase_id:
                purchase = Purchase.objects.get(id=purchase_id)
                payment = pay_supplier(
                    purchase=purchase,
                    amount=amount,
                    payment_date=payment_date,
                    payment_method=payment_method,
                    received_by=request.user,
                    transaction_id=transaction_id,
                    reference_no=reference_no,
                    note=note,
                )

            else:
                supplier = Supplier.objects.get(id=supplier_id)
                payment = supplier_advance_payment(
                    supplier=supplier,
                    amount=amount,
                    payment_date=payment_date,
                    payment_method=payment_method,
                    received_by=request.user,
                    transaction_id=transaction_id,
                    reference_no=reference_no,
                    note=note,
                )

        serializer = self.get_serializer(payment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)