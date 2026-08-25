from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import (
    IsManager,
    IsStaff,
)

from .models import Payment
from .serializers import PaymentSerializer
from .services import (
    pay_supplier,
    receive_customer_advance,
    receive_customer_payment,
    supplier_advance_payment,
)

from sales.models import Sale
from purchases.models import Purchase
from customers.models import Customer
from suppliers.models import Supplier


# ==========================================================
# PAYMENT VIEWSET
# ==========================================================


class PaymentViewSet(viewsets.ModelViewSet):

    queryset = (
        Payment.objects
        .select_related(
            "customer",
            "supplier",
            "sale",
            "purchase",
            "received_by",
        )
        .all()
        .order_by("-payment_date", "-id")
    )

    serializer_class = PaymentSerializer

    # ------------------------------------------------------
    # ROLE BASED PERMISSION
    # ------------------------------------------------------

    def get_permissions(self):

        # CREATE
        #
        # ADMIN + MANAGER only.
        if self.action == "create":
            return [
                IsAuthenticated(),
                IsManager(),
            ]

        # LIST / RETRIEVE
        #
        # ADMIN + MANAGER + STAFF.
        return [
            IsAuthenticated(),
            IsStaff(),
        ]

    # ------------------------------------------------------
    # CREATE PAYMENT
    # ------------------------------------------------------

    def create(self, request, *args, **kwargs):

        data = request.data

        payment_type = data.get("payment_type")
        amount = data.get("amount")
        payment_date = data.get("payment_date")

        payment_method = data.get(
            "payment_method",
            "CASH",
        )

        reference_no = data.get(
            "reference_no",
            "",
        )

        transaction_id = data.get(
            "transaction_id",
            "",
        )

        note = data.get(
            "note",
            "",
        )

        sale_id = data.get("sale")
        purchase_id = data.get("purchase")

        customer_id = data.get("customer")
        supplier_id = data.get("supplier")

        # ==================================================
        # CUSTOMER PAYMENT
        # ==================================================

        if payment_type == "CUSTOMER":

            # ----------------------------------------------
            # PAYMENT AGAINST SALE
            # ----------------------------------------------

            if sale_id:

                try:
                    sale = Sale.objects.get(
                        id=sale_id
                    )
                except Sale.DoesNotExist:
                    raise ValidationError(
                        {
                            "sale": "Sale not found."
                        }
                    )

                try:

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

                except ValueError as exc:

                    raise ValidationError(
                        {
                            "amount": str(exc)
                        }
                    )

            # ----------------------------------------------
            # CUSTOMER ADVANCE
            # ----------------------------------------------

            else:

                if not customer_id:
                    raise ValidationError(
                        {
                            "customer": (
                                "Customer is required "
                                "for advance payment."
                            )
                        }
                    )

                try:
                    customer = Customer.objects.get(
                        id=customer_id
                    )
                except Customer.DoesNotExist:
                    raise ValidationError(
                        {
                            "customer": "Customer not found."
                        }
                    )

                try:

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

                except ValueError as exc:

                    raise ValidationError(
                        {
                            "amount": str(exc)
                        }
                    )

        # ==================================================
        # SUPPLIER PAYMENT
        # ==================================================

        elif payment_type == "SUPPLIER":

            # ----------------------------------------------
            # PAYMENT AGAINST PURCHASE
            # ----------------------------------------------

            if purchase_id:

                try:
                    purchase = Purchase.objects.get(
                        id=purchase_id
                    )
                except Purchase.DoesNotExist:
                    raise ValidationError(
                        {
                            "purchase": (
                                "Purchase not found."
                            )
                        }
                    )

                try:

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

                except ValueError as exc:

                    raise ValidationError(
                        {
                            "amount": str(exc)
                        }
                    )

            # ----------------------------------------------
            # SUPPLIER ADVANCE
            # ----------------------------------------------

            else:

                if not supplier_id:
                    raise ValidationError(
                        {
                            "supplier": (
                                "Supplier is required "
                                "for advance payment."
                            )
                        }
                    )

                try:
                    supplier = Supplier.objects.get(
                        id=supplier_id
                    )
                except Supplier.DoesNotExist:
                    raise ValidationError(
                        {
                            "supplier": "Supplier not found."
                        }
                    )

                try:

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

                except ValueError as exc:

                    raise ValidationError(
                        {
                            "amount": str(exc)
                        }
                    )

        # ==================================================
        # INVALID PAYMENT TYPE
        # ==================================================

        else:

            raise ValidationError(
                {
                    "payment_type": (
                        "Payment type must be "
                        "'CUSTOMER' or 'SUPPLIER'."
                    )
                }
            )

        serializer = self.get_serializer(payment)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    # ------------------------------------------------------
    # UPDATE NOT ALLOWED
    # ------------------------------------------------------

    def update(self, request, *args, **kwargs):

        return Response(
            {
                "detail": (
                    "Payment records cannot be updated."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # ------------------------------------------------------
    # PARTIAL UPDATE NOT ALLOWED
    # ------------------------------------------------------

    def partial_update(
        self,
        request,
        *args,
        **kwargs,
    ):

        return Response(
            {
                "detail": (
                    "Payment records cannot be updated."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # ------------------------------------------------------
    # DELETE NOT ALLOWED
    # ------------------------------------------------------

    def destroy(self, request, *args, **kwargs):

        return Response(
            {
                "detail": (
                    "Payment records cannot be deleted."
                )
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

