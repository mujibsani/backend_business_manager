
from decimal import Decimal
from datetime import date

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User

from customers.models import Customer
from products.models import Product, Category
from sales.models import Sale, SaleItem

from sales_returns.models import (
    SalesReturn,
    SalesReturnItem,
)


class SalesReturnAPITests(TestCase):

    def setUp(self):

        self.client = APIClient()

        # ==================================================
        # CATEGORY
        # ==================================================

        self.category = Category.objects.create(
            name="Test Category"
        )

        # ==================================================
        # PRODUCT
        # ==================================================

        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            cost_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock=Decimal("10.00"),
            min_stock=Decimal("2.00"),
        )

        # ==================================================
        # CUSTOMER
        # ==================================================

        self.customer = Customer.objects.create(
            name="Test Customer",
            phone="01711111111",
        )

        # ==================================================
        # SALE
        # ==================================================

        self.sale = Sale.objects.create(
            invoice_no="SALE-TEST-001",
            customer=self.customer,
            date=date.today(),
            total_amount=Decimal("500.00"),
            paid_amount=Decimal("500.00"),
            due_amount=Decimal("0.00"),
            status="PAID",
        )

        self.sale_item = SaleItem.objects.create(
            sale=self.sale,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
        )

        self.sale.update_totals()

        # ==================================================
        # USERS
        # ==================================================

        self.admin = User.objects.create_user(
            username="sales_return_admin",
            password="AdminPass123",
            role=User.Role.ADMIN,
        )

        self.manager = User.objects.create_user(
            username="sales_return_manager",
            password="ManagerPass123",
            role=User.Role.MANAGER,
        )

        self.staff = User.objects.create_user(
            username="sales_return_staff",
            password="StaffPass123",
            role=User.Role.STAFF,
        )

        # ==================================================
        # URL
        # ==================================================

        self.url = reverse(
            "sales_returns:sales-return-list-create"
        )

    # ======================================================
    # HELPER
    # ======================================================

    def valid_payload(
        self,
        quantity="2.00",
        refund_amount="0.00",
    ):

        return {
            "sale": self.sale.id,
            "date": str(date.today()),
            "refund_amount": refund_amount,
            "reason": "Customer return",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": quantity,
                    "unit_price": "100.00",
                }
            ],
        }

    # ======================================================
    # AUTHENTICATION
    # ======================================================

    def test_list_requires_authentication(self):

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_create_requires_authentication(self):

        response = self.client.post(
            self.url,
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ======================================================
    # ADMIN
    # ======================================================

    def test_admin_can_list_sales_returns(self):

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_admin_can_create_sales_return(self):

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.url,
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            SalesReturn.objects.count(),
            1,
        )

        sales_return = SalesReturn.objects.first()

        self.assertEqual(
            sales_return.total_amount,
            Decimal("200.00"),
        )

        self.assertEqual(
            sales_return.created_by,
            self.admin,
        )

    def test_admin_can_create_return_with_refund(self):

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.url,
            self.valid_payload(
                quantity="2.00",
                refund_amount="100.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        sales_return = SalesReturn.objects.first()

        self.assertEqual(
            sales_return.refund_amount,
            Decimal("100.00"),
        )

    # ======================================================
    # MANAGER
    # ======================================================

    def test_manager_can_list_sales_returns(self):

        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_manager_can_create_sales_return(self):

        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.post(
            self.url,
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            SalesReturn.objects.count(),
            1,
        )

    # ======================================================
    # STAFF
    # ======================================================

    def test_staff_can_list_sales_returns(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_staff_can_create_sales_return(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            self.url,
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            SalesReturn.objects.count(),
            1,
        )

        sales_return = SalesReturn.objects.first()

        self.assertEqual(
            sales_return.created_by,
            self.staff,
        )

    # ======================================================
    # RETRIEVE
    # ======================================================

    def test_admin_can_retrieve_sales_return(self):

        self.client.force_authenticate(
            user=self.admin
        )

        create_response = self.client.post(
            self.url,
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        sales_return = SalesReturn.objects.first()

        detail_url = reverse(
            "sales_returns:sales-return-detail",
            kwargs={
                "pk": sales_return.pk
            },
        )

        response = self.client.get(
            detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_staff_can_retrieve_sales_return(self):

        self.client.force_authenticate(
            user=self.staff
        )

        create_response = self.client.post(
            self.url,
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        sales_return = SalesReturn.objects.first()

        detail_url = reverse(
            "sales_returns:sales-return-detail",
            kwargs={
                "pk": sales_return.pk
            },
        )

        response = self.client.get(
            detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ======================================================
    # VALIDATION
    # ======================================================

    def test_missing_sale_is_rejected(self):

        self.client.force_authenticate(
            user=self.admin
        )

        payload = self.valid_payload()

        payload.pop("sale")

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_missing_items_is_rejected(self):

        self.client.force_authenticate(
            user=self.admin
        )

        payload = self.valid_payload()

        payload.pop("items")

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_negative_quantity_is_rejected_by_api(self):

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.url,
            self.valid_payload(
                quantity="-1.00"
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_zero_quantity_is_rejected_by_api(self):

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.url,
            self.valid_payload(
                quantity="0.00"
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )