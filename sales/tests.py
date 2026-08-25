from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from cashbook.models import CashbookEntry
from customers.models import Customer
from products.models import Product, StockLog

from .models import Sale, SaleItem


User = get_user_model()


class SalesAPITests(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin",
            password="AdminPass123",
            role=User.Role.ADMIN,
        )

        self.manager = User.objects.create_user(
            username="manager",
            password="ManagerPass123",
            role=User.Role.MANAGER,
        )

        self.staff = User.objects.create_user(
            username="staff",
            password="StaffPass123",
            role=User.Role.STAFF,
        )

        self.customer = Customer.objects.create(
            name="Test Customer",
        )

        self.product = Product.objects.create(
            name="Test Product",
            cost_price=Decimal("50.00"),
            selling_price=Decimal("100.00"),
            stock=Decimal("20.00"),
            min_stock=Decimal("5.00"),
        )

    # ======================================================
    # AUTHENTICATION
    # ======================================================

    def test_create_sale_requires_authentication(self):

        response = self.client.post(
            "/api/sales/create/",
            {
                "customer_id": self.customer.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": "2",
                        "unit_price": "100.00",
                    }
                ],
                "paid_amount": "100.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    # ======================================================
    # ROLE ACCESS
    # ======================================================

    def test_admin_can_create_sale(self):

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            "/api/sales/create/",
            {
                "customer_id": self.customer.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": "2",
                        "unit_price": "100.00",
                    }
                ],
                "paid_amount": "100.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_manager_can_create_sale(self):

        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.post(
            "/api/sales/create/",
            {
                "customer_id": self.customer.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": "2",
                        "unit_price": "100.00",
                    }
                ],
                "paid_amount": "100.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    def test_staff_can_create_sale(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            "/api/sales/create/",
            {
                "customer_id": self.customer.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": "2",
                        "unit_price": "100.00",
                    }
                ],
                "paid_amount": "100.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

    # ======================================================
    # CREATE SALE
    # ======================================================

    def test_sale_is_created(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            "/api/sales/create/",
            {
                "customer_id": self.customer.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": "2",
                        "unit_price": "100.00",
                    }
                ],
                "paid_amount": "100.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        sale = Sale.objects.get()

        self.assertEqual(
            sale.total_amount,
            Decimal("200.00"),
        )

        self.assertEqual(
            sale.paid_amount,
            Decimal("100.00"),
        )

        self.assertEqual(
            sale.due_amount,
            Decimal("100.00"),
        )

        self.assertEqual(
            sale.status,
            "PARTIAL",
        )

    # ======================================================
    # STOCK
    # ======================================================

    def test_stock_decreases_once(self):

        self.client.force_authenticate(
            user=self.staff
        )

        self.client.post(
            "/api/sales/create/",
            {
                "customer_id": self.customer.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": "3",
                        "unit_price": "100.00",
                    }
                ],
                "paid_amount": "300.00",
            },
            format="json",
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal("17.00"),
        )

        self.assertEqual(
            StockLog.objects.filter(
                product=self.product,
                type="OUT",
            ).count(),
            1,
        )

    # ======================================================
    # INSUFFICIENT STOCK
    # ======================================================

    def test_insufficient_stock_fails(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            "/api/sales/create/",
            {
                "customer_id": self.customer.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": "100",
                        "unit_price": "100.00",
                    }
                ],
                "paid_amount": "0",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            Sale.objects.count(),
            0,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal("20.00"),
        )

    # ======================================================
    # PAID AMOUNT
    # ======================================================

    def test_paid_amount_cannot_exceed_total(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            "/api/sales/create/",
            {
                "customer_id": self.customer.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": "2",
                        "unit_price": "100.00",
                    }
                ],
                "paid_amount": "500.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            Sale.objects.count(),
            0,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            Decimal("20.00"),
        )

    # ======================================================
    # CUSTOMER REQUIRED
    # ======================================================

    def test_customer_is_required(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            "/api/sales/create/",
            {
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": "2",
                        "unit_price": "100.00",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    # ======================================================
    # LIST
    # ======================================================

    def test_authenticated_user_can_list_sales(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.get(
            "/api/sales/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # ======================================================
    # DETAIL
    # ======================================================

    def test_authenticated_user_can_view_sale(self):

        sale = Sale.objects.create(
            customer=self.customer,
            invoice_no="SALE-TEST-001",
            sales_person=self.staff,
            date="2026-08-26",
            total_amount=Decimal("100.00"),
            paid_amount=Decimal("0.00"),
            due_amount=Decimal("100.00"),
            status="UNPAID",
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.get(
            f"/api/sales/{sale.id}/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # ======================================================
    # DETAIL NOT FOUND
    # ======================================================

    def test_sale_detail_not_found(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.get(
            "/api/sales/999999/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )