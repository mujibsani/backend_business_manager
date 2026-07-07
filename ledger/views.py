from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from customers.models import Customer
from suppliers.models import Supplier

from .models import LedgerEntry
from .serializers import LedgerEntrySerializer
from .services import (
    get_customer_statement,
    get_supplier_statement,
)


# ==========================================================
# ALL LEDGER ENTRIES
# ==========================================================

class LedgerEntryListAPIView(APIView):
    """
    List all ledger entries.
    """

    def get(self, request):

        queryset = LedgerEntry.objects.all().order_by("-date", "-id")

        serializer = LedgerEntrySerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)


# ==========================================================
# SINGLE LEDGER ENTRY
# ==========================================================

class LedgerEntryDetailAPIView(APIView):
    """
    Retrieve a single ledger entry.
    """

    def get(self, request, pk):

        entry = get_object_or_404(
            LedgerEntry,
            pk=pk
        )

        serializer = LedgerEntrySerializer(entry)

        return Response(serializer.data)


# ==========================================================
# CUSTOMER LEDGER STATEMENT
# ==========================================================

class CustomerLedgerStatementAPIView(APIView):
    """
    Customer Ledger Statement
    """

    def get(self, request, customer_id):

        customer = get_object_or_404(
            Customer,
            pk=customer_id
        )

        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        statement = get_customer_statement(
            customer=customer,
            from_date=from_date,
            to_date=to_date,
        )

        return Response(
            {
                "customer": customer.name,
                "opening_balance": statement["opening_balance"],
                "closing_balance": statement["closing_balance"],
                "transactions": statement["transactions"],
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# SUPPLIER LEDGER STATEMENT
# ==========================================================

class SupplierLedgerStatementAPIView(APIView):
    """
    Supplier Ledger Statement
    """

    def get(self, request, supplier_id):

        supplier = get_object_or_404(
            Supplier,
            pk=supplier_id
        )

        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        statement = get_supplier_statement(
            supplier=supplier,
            from_date=from_date,
            to_date=to_date,
        )

        return Response(
            {
                "supplier": supplier.name,
                "opening_balance": statement["opening_balance"],
                "closing_balance": statement["closing_balance"],
                "transactions": statement["transactions"],
            },
            status=status.HTTP_200_OK,
        )