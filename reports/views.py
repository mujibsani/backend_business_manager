from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .services import (
    get_dashboard_summary,

    get_sales_summary,
    get_daily_sales,
    get_weekly_sales,
    get_monthly_sales,

    get_purchase_summary,
    get_daily_purchases,
    get_weekly_purchases,
    get_monthly_purchases,

    get_expense_summary,
    get_daily_expenses,
    get_monthly_expenses,

    get_inventory_report_summary,
    get_low_stock_products,
    get_inventory_value,

    get_profit_summary,
    get_cash_flow_summary,
)


# ==========================================================
# DASHBOARD
# ==========================================================

class DashboardAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response(
            get_dashboard_summary()
        )


# ==========================================================
# SALES REPORT
# ==========================================================

class SalesReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "summary": get_sales_summary(),
            "daily": get_daily_sales(),
            "weekly": get_weekly_sales(),
            "monthly": get_monthly_sales(),
        })


# ==========================================================
# PURCHASE REPORT
# ==========================================================

class PurchaseReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "summary": get_purchase_summary(),
            "daily": get_daily_purchases(),
            "weekly": get_weekly_purchases(),
            "monthly": get_monthly_purchases(),
        })


# ==========================================================
# EXPENSE REPORT
# ==========================================================

class ExpenseReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "summary": get_expense_summary(),
            "daily": get_daily_expenses(),
            "monthly": get_monthly_expenses(),
        })


# ==========================================================
# INVENTORY REPORT
# ==========================================================

class InventoryReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "summary": get_inventory_report_summary(),
            "inventory_value": get_inventory_value(),
            "low_stock_products": get_low_stock_products(),
        })


# ==========================================================
# FINANCE REPORT
# ==========================================================

class FinanceReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "profit": get_profit_summary(),
            "cash_flow": get_cash_flow_summary(),
        })