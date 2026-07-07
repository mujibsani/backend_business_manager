from rest_framework import serializers

from .models import LedgerEntry


# ==========================================================
# LEDGER ENTRY SERIALIZER
# ==========================================================

class LedgerEntrySerializer(serializers.ModelSerializer):

    party_name = serializers.SerializerMethodField()

    class Meta:
        model = LedgerEntry

        fields = (
            "id",
            "date",
            "party_type",
            "party_name",
            "reference_type",
            "reference_no",
            "description",
            "debit",
            "credit",
            "balance",
        )

    def get_party_name(self, obj):

        if obj.customer:
            return obj.customer.name

        if obj.supplier:
            return obj.supplier.name

        return ""


# ==========================================================
# CUSTOMER LEDGER TRANSACTION
# ==========================================================

class CustomerLedgerTransactionSerializer(serializers.Serializer):

    date = serializers.DateField()

    reference_type = serializers.CharField()

    reference_no = serializers.CharField()

    description = serializers.CharField()

    debit = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    credit = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    balance = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )


# ==========================================================
# CUSTOMER STATEMENT
# ==========================================================

class CustomerStatementSerializer(serializers.Serializer):

    customer = serializers.CharField()

    opening_balance = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    closing_balance = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    transactions = CustomerLedgerTransactionSerializer(
        many=True
    )


# ==========================================================
# SUPPLIER LEDGER TRANSACTION
# ==========================================================

class SupplierLedgerTransactionSerializer(serializers.Serializer):

    date = serializers.DateField()

    reference_type = serializers.CharField()

    reference_no = serializers.CharField()

    description = serializers.CharField()

    debit = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    credit = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    balance = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )


# ==========================================================
# SUPPLIER STATEMENT
# ==========================================================

class SupplierStatementSerializer(serializers.Serializer):

    supplier = serializers.CharField()

    opening_balance = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    closing_balance = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    transactions = SupplierLedgerTransactionSerializer(
        many=True
    )

class StatementSerializer(serializers.Serializer):

    party = serializers.CharField()

    opening_balance = serializers.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    closing_balance = serializers.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    transactions = LedgerEntrySerializer(many=True)