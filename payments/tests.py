from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer
from suppliers.models import Supplier
from products.models import Product, Category
from sales.models import Sale, SaleItem
from purchases.models import Purchase, PurchaseItem
from payments.models import Payment


User = get_user_model()


class PaymentAPITests(APITestCase):

    # ==========================================================
    # SETUP
    # ==========================================================

    def setUp(self):

        # ------------------------------------------------------
        # USERS
        # ------------------------------------------------------

        self.admin_user = User.objects.create_user(
            username="payment_admin",
            password="AdminPass123",
        )

        self.manager_user = User.objects.create_user(
            username="payment_manager",
            password="ManagerPass123",
        )

        self.staff_user = User.objects.create_user(
            username="payment_staff",
            password="StaffPass123",
        )

        # Support common role implementations.
        self._set_role(self.admin_user, "ADMIN")
        self._set_role(self.manager_user, "MANAGER")
        self._set_role(self.staff_user, "STAFF")

        # ------------------------------------------------------
        # CUSTOMER
        # ------------------------------------------------------

        self.customer = Customer.objects.create(
            name="Test Customer",
        )

        # ------------------------------------------------------
        # SUPPLIER
        # ------------------------------------------------------

        self.supplier = Supplier.objects.create(
            name="Test Supplier",
        )

        # ------------------------------------------------------
        # PRODUCT
        # ------------------------------------------------------

        self.category = Category.objects.create(
            name="Test Category",
        )

        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            cost_price=Decimal("50.00"),
            selling_price=Decimal("100.00"),
            stock=Decimal("100.00"),
            min_stock=Decimal("10.00"),
        )

        # ------------------------------------------------------
        # SALE
        # ------------------------------------------------------

        self.sale = Sale.objects.create(
            invoice_no="SALE-TEST-001",
            customer=self.customer,
            date=date.today(),
            total_amount=Decimal("1000.00"),
            paid_amount=Decimal("0.00"),
            due_amount=Decimal("1000.00"),
            status="UNPAID",
        )

        SaleItem.objects.create(
            sale=self.sale,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            subtotal=Decimal("1000.00"),
        )

        # ------------------------------------------------------
        # PURCHASE
        # ------------------------------------------------------

        self.purchase = Purchase.objects.create(
            invoice_no="PUR-TEST-001",
            supplier=self.supplier,
            date=date.today(),
            total_amount=Decimal("800.00"),
            paid_amount=Decimal("0.00"),
            due_amount=Decimal("800.00"),
            status="UNPAID",
        )

        PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal("10.00"),
            unit_price=Decimal("80.00"),
            subtotal=Decimal("800.00"),
        )

        self.url = reverse("payments:payments-list")

    # ==========================================================
    # ROLE HELPER
    # ==========================================================

    def _set_role(self, user, role):

        """
        Supports projects where role is stored either directly
        on User or through a profile.

        If your User model uses a different role field,
        adjust only this helper.
        """

        if hasattr(user, "role"):

            user.role = role
            user.save()

            return

        if hasattr(user, "userprofile"):

            profile = user.userprofile

            if hasattr(profile, "role"):

                profile.role = role
                profile.save()

                return

        if hasattr(user, "profile"):

            profile = user.profile

            if hasattr(profile, "role"):

                profile.role = role
                profile.save()

                return

    # ==========================================================
    # AUTHENTICATION
    # ==========================================================

    def authenticate(self, user):

        self.client.force_authenticate(user=user)

    # ==========================================================
    # CUSTOMER PAYMENT
    # ==========================================================

    def test_admin_can_create_customer_payment(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "sale": self.sale.id,
                "amount": "300.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
                "reference_no": "REF-001",
                "note": "Customer payment",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Payment.objects.count(),
            1,
        )

    def test_manager_can_create_customer_payment(self):

        self.authenticate(self.manager_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "sale": self.sale.id,
                "amount": "300.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_staff_cannot_create_customer_payment(self):

        self.authenticate(self.staff_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "sale": self.sale.id,
                "amount": "300.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # SUPPLIER PAYMENT
    # ==========================================================

    def test_admin_can_create_supplier_payment(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "SUPPLIER",
                "purchase": self.purchase.id,
                "amount": "300.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_manager_can_create_supplier_payment(self):

        self.authenticate(self.manager_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "SUPPLIER",
                "purchase": self.purchase.id,
                "amount": "300.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_staff_cannot_create_supplier_payment(self):

        self.authenticate(self.staff_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "SUPPLIER",
                "purchase": self.purchase.id,
                "amount": "300.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # CUSTOMER ADVANCE
    # ==========================================================

    def test_customer_advance_payment(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "customer": self.customer.id,
                "amount": "250.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        payment = Payment.objects.get(
            payment_no=response.data["payment_no"]
        )

        self.assertEqual(
            payment.customer,
            self.customer,
        )

        self.assertIsNone(
            payment.sale,
        )

    # ==========================================================
    # SUPPLIER ADVANCE
    # ==========================================================

    def test_supplier_advance_payment(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "SUPPLIER",
                "supplier": self.supplier.id,
                "amount": "250.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        payment = Payment.objects.get(
            payment_no=response.data["payment_no"]
        )

        self.assertEqual(
            payment.supplier,
            self.supplier,
        )

        self.assertIsNone(
            payment.purchase,
        )

    # ==========================================================
    # SALE UPDATE
    # ==========================================================

    def test_customer_payment_updates_sale(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "sale": self.sale.id,
                "amount": "300.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.sale.refresh_from_db()

        self.assertEqual(
            self.sale.paid_amount,
            Decimal("300.00"),
        )

        self.assertEqual(
            self.sale.due_amount,
            Decimal("700.00"),
        )

        self.assertEqual(
            self.sale.status,
            "PARTIAL",
        )

    def test_full_customer_payment_marks_sale_paid(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "sale": self.sale.id,
                "amount": "1000.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.sale.refresh_from_db()

        self.assertEqual(
            self.sale.paid_amount,
            Decimal("1000.00"),
        )

        self.assertEqual(
            self.sale.due_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            self.sale.status,
            "PAID",
        )

    # ==========================================================
    # PURCHASE UPDATE
    # ==========================================================

    def test_supplier_payment_updates_purchase(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "SUPPLIER",
                "purchase": self.purchase.id,
                "amount": "300.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.paid_amount,
            Decimal("300.00"),
        )

        self.assertEqual(
            self.purchase.due_amount,
            Decimal("500.00"),
        )

        self.assertEqual(
            self.purchase.status,
            "PARTIAL",
        )

    def test_full_supplier_payment_marks_purchase_paid(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "SUPPLIER",
                "purchase": self.purchase.id,
                "amount": "800.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.paid_amount,
            Decimal("800.00"),
        )

        self.assertEqual(
            self.purchase.due_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            self.purchase.status,
            "PAID",
        )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def test_negative_amount_is_rejected(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "sale": self.sale.id,
                "amount": "-100.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_zero_amount_is_rejected(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "sale": self.sale.id,
                "amount": "0.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_payment_cannot_exceed_sale_due(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "sale": self.sale.id,
                "amount": "1500.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_payment_cannot_exceed_purchase_due(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "SUPPLIER",
                "purchase": self.purchase.id,
                "amount": "1000.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_customer_payment_requires_customer_or_sale(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "amount": "100.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_supplier_payment_requires_supplier_or_purchase(self):

        self.authenticate(self.admin_user)

        response = self.client.post(
            self.url,
            {
                "payment_type": "SUPPLIER",
                "amount": "100.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ==========================================================
    # AUTHENTICATION
    # ==========================================================

    def test_create_requires_authentication(self):

        response = self.client.post(
            self.url,
            {
                "payment_type": "CUSTOMER",
                "sale": self.sale.id,
                "amount": "100.00",
                "payment_method": "CASH",
                "payment_date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_list_requires_authentication(self):

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ==========================================================
    # LIST
    # ==========================================================

    def test_admin_can_list_payments(self):

        self.authenticate(self.admin_user)

        Payment.objects.create(
            payment_no="PAY-TEST-001",
            payment_type="CUSTOMER",
            customer=self.customer,
            sale=self.sale,
            amount=Decimal("100.00"),
            payment_method="CASH",
            payment_date=date.today(),
            received_by=self.admin_user,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_manager_can_list_payments(self):

        self.authenticate(self.manager_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_staff_can_list_payments(self):

        self.authenticate(self.staff_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ==========================================================
    # RETRIEVE
    # ==========================================================

    def test_admin_can_retrieve_payment(self):

        payment = Payment.objects.create(
            payment_no="PAY-TEST-002",
            payment_type="CUSTOMER",
            customer=self.customer,
            sale=self.sale,
            amount=Decimal("100.00"),
            payment_method="CASH",
            payment_date=date.today(),
            received_by=self.admin_user,
        )

        self.authenticate(self.admin_user)

        response = self.client.get(
            reverse(
                "payments:payments-detail",
                kwargs={"pk": payment.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_staff_can_retrieve_payment(self):

        payment = Payment.objects.create(
            payment_no="PAY-TEST-003",
            payment_type="CUSTOMER",
            customer=self.customer,
            sale=self.sale,
            amount=Decimal("100.00"),
            payment_method="CASH",
            payment_date=date.today(),
            received_by=self.admin_user,
        )

        self.authenticate(self.staff_user)

        response = self.client.get(
            reverse(
                "payments:payments-detail",
                kwargs={"pk": payment.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ==========================================================
    # UPDATE / DELETE
    # ==========================================================

    def test_payment_update_is_not_allowed(self):

        payment = Payment.objects.create(
            payment_no="PAY-TEST-004",
            payment_type="CUSTOMER",
            customer=self.customer,
            sale=self.sale,
            amount=Decimal("100.00"),
            payment_method="CASH",
            payment_date=date.today(),
            received_by=self.admin_user,
        )

        self.authenticate(self.admin_user)

        response = self.client.patch(
            reverse(
                "payments:payments-detail",
                kwargs={"pk": payment.pk},
            ),
            {
                "amount": "200.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_payment_delete_is_not_allowed(self):

        payment = Payment.objects.create(
            payment_no="PAY-TEST-005",
            payment_type="CUSTOMER",
            customer=self.customer,
            sale=self.sale,
            amount=Decimal("100.00"),
            payment_method="CASH",
            payment_date=date.today(),
            received_by=self.admin_user,
        )

        self.authenticate(self.admin_user)

        response = self.client.delete(
            reverse(
                "payments:payments-detail",
                kwargs={"pk": payment.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )