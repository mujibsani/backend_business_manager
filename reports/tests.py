from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()

class ReportsAuthenticationTests(APITestCase):
    """
    Verify that report endpoints require authentication.
    """

    def setUp(self):

        self.endpoints = [
            "/api/dashboard/",
            "/api/sales/",
            "/api/purchases/",
            "/api/expenses/",
            "/api/inventory/",
            "/api/finance/",
        ]

    def test_report_endpoints_require_authentication(self):

        for endpoint in self.endpoints:

            with self.subTest(endpoint=endpoint):

                response = self.client.get(endpoint)

                self.assertIn(
                    response.status_code,
                    (
                        status.HTTP_401_UNAUTHORIZED,
                        status.HTTP_403_FORBIDDEN,
                    ),
                    msg=(
                        f"{endpoint} returned "
                        f"{response.status_code}"
                    ),
                )

class ReportsAuthenticatedTests(APITestCase):
    """
    Verify that authenticated users can access reports.
    """

    def setUp(self):

        self.user = User.objects.create_user(
            username="report_test_user",
            password="TestPassword123",
            role=User.Role.STAFF,
        )

        self.client.force_authenticate(
            user=self.user
        )

    # ======================================================
    # DASHBOARD
    # ======================================================

    def test_dashboard_report(self):

        response = self.client.get(
            "/api/dashboard/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "today",
            response.data,
        )

        self.assertIn(
            "month",
            response.data,
        )

        self.assertIn(
            "cash",
            response.data,
        )

        self.assertIn(
            "inventory",
            response.data,
        )

        self.assertIn(
            "parties",
            response.data,
        )

    # ======================================================
    # SALES
    # ======================================================

    def test_sales_report(self):

        response = self.client.get(
            "/api/sales/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "summary",
            response.data,
        )

        self.assertIn(
            "daily",
            response.data,
        )

        self.assertIn(
            "weekly",
            response.data,
        )

        self.assertIn(
            "monthly",
            response.data,
        )

    # ======================================================
    # PURCHASES
    # ======================================================

    def test_purchase_report(self):

        response = self.client.get(
            "/api/purchases/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "summary",
            response.data,
        )

        self.assertIn(
            "daily",
            response.data,
        )

        self.assertIn(
            "weekly",
            response.data,
        )

        self.assertIn(
            "monthly",
            response.data,
        )

    # ======================================================
    # EXPENSES
    # ======================================================

    def test_expense_report(self):

        response = self.client.get(
            "/api/expenses/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "summary",
            response.data,
        )

        self.assertIn(
            "daily",
            response.data,
        )

        self.assertIn(
            "monthly",
            response.data,
        )

    # ======================================================
    # INVENTORY
    # ======================================================

    def test_inventory_report(self):

        response = self.client.get(
            "/api/inventory/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "summary",
            response.data,
        )

        self.assertIn(
            "inventory_value",
            response.data,
        )

        self.assertIn(
            "low_stock_products",
            response.data,
        )

    # ======================================================
    # FINANCE
    # ======================================================

    def test_finance_report(self):

        response = self.client.get(
            "/api/finance/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "profit",
            response.data,
        )

        self.assertIn(
            "cash_flow",
            response.data,
        )