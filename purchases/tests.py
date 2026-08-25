from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from cashbook.models import CashbookEntry
from customers.models import Customer
from products.models import Category, Product
from suppliers.models import Supplier

from .models import Purchase, PurchaseItem


User = get_user_model()


class PurchaseAPITests(APITestCase):
    """
    Complete Purchase API test suite.

    Covers:
        - Authentication
        - Role-based access
        - Purchase creation
        - Purchase listing
        - Purchase detail
        - Purchase items
        - Stock increase
        - Total calculation
        - Due calculation
        - Payment status
        - Cashbook
        - Validation
    """

    # ======================================================
    # SETUP
    # ======================================================

    def setUp(self):

        self.admin = User.objects.create_user(
            username="purchase_admin",
            password="AdminPass123",
        )

        self.manager = User.objects.create_user(
            username="purchase_manager",
            password="ManagerPass123",
        )

        self.staff = User.objects.create_user(
            username="purchase_staff",
            password="StaffPass123",
        )

        # --------------------------------------------------
        # Assign roles
        # --------------------------------------------------

        if hasattr(self.admin, "role"):
            self.admin.role = "ADMIN"
            self.admin.save(update_fields=["role"])

        if hasattr(self.manager, "role"):
            self.manager.role = "MANAGER"
            self.manager.save(update_fields=["role"])

        if hasattr(self.staff, "role"):
            self.staff.role = "STAFF"
            self.staff.save(update_fields=["role"])

        # --------------------------------------------------
        # Supplier
        # --------------------------------------------------

        self.supplier = Supplier.objects.create(
            name="Test Supplier",
        )

        # --------------------------------------------------
        # Customer
        # --------------------------------------------------

        self.customer = Customer.objects.create(
            name="Test Customer",
        )

        # --------------------------------------------------
        # Category
        # --------------------------------------------------

        self.category = Category.objects.create(
            name="Test Category",
        )

        # --------------------------------------------------
        # Product
        # --------------------------------------------------

        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            cost_price=Decimal("50.00"),
            selling_price=Decimal("100.00"),
            stock=Decimal("10.00"),
            min_stock=Decimal("2.00"),
        )

    # ======================================================
    # URL HELPERS
    # ======================================================

    def purchase_list_url(self):

        return reverse(
            "purchases:purchase-list"
        )

    def purchase_detail_url(self, purchase_id):

        return reverse(
            "purchases:purchase-detail",
            kwargs={
                "pk": purchase_id,
            },
        )

    # ======================================================
    # AUTHENTICATION HELPERS
    # ======================================================

    def authenticate(self, user):

        self.client.force_authenticate(
            user=user
        )

    def unauthenticate(self):

        self.client.force_authenticate(
            user=None
        )

    # ======================================================
    # PAYLOAD
    # ======================================================

    def purchase_payload(
        self,
        invoice_no="PUR-TEST-001",
        quantity="2",
        unit_price="50.00",
        paid_amount="0.00",
    ):

        return {
            "supplier_id": self.supplier.id,
            "invoice_no": invoice_no,
            "date": "2026-08-26",
            "paid_amount": paid_amount,
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                }
            ],
        }

    # ======================================================
    # AUTHENTICATION
    # ======================================================

    def test_purchase_list_requires_authentication(self):

        self.unauthenticate()

        response = self.client.get(
            self.purchase_list_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_purchase_create_requires_authentication(self):

        self.unauthenticate()

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ======================================================
    # ROLE - LIST
    # ======================================================

    def test_admin_can_list_purchases(self):

        self.authenticate(self.admin)

        response = self.client.get(
            self.purchase_list_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_manager_can_list_purchases(self):

        self.authenticate(self.manager)

        response = self.client.get(
            self.purchase_list_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_staff_can_list_purchases(self):

        self.authenticate(self.staff)

        response = self.client.get(
            self.purchase_list_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ======================================================
    # ROLE - CREATE
    # ======================================================

    def test_admin_can_create_purchase(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-ADMIN-001"
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Purchase.objects.filter(
                invoice_no="PUR-ADMIN-001"
            ).exists()
        )

    def test_manager_can_create_purchase(self):

        self.authenticate(self.manager)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-MANAGER-001"
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_staff_can_create_purchase(self):

        self.authenticate(self.staff)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-STAFF-001"
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    # ======================================================
    # PURCHASE ITEM
    # ======================================================

    def test_purchase_creates_purchase_item(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-ITEM-001",
                quantity="3",
                unit_price="75.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        purchase = Purchase.objects.get(
            invoice_no="PUR-ITEM-001"
        )

        self.assertEqual(
            PurchaseItem.objects.filter(
                purchase=purchase
            ).count(),
            1,
        )

        item = PurchaseItem.objects.get(
            purchase=purchase
        )

        self.assertEqual(
            item.quantity,
            Decimal("3.00"),
        )

        self.assertEqual(
            item.unit_price,
            Decimal("75.00"),
        )

        self.assertEqual(
            item.subtotal,
            Decimal("225.00"),
        )

    # ======================================================
    # STOCK
    # ======================================================

    def test_purchase_increases_stock(self):

        self.authenticate(self.admin)

        initial_stock = self.product.stock

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-STOCK-001",
                quantity="5",
                unit_price="50.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            initial_stock + Decimal("5.00"),
        )

    # ======================================================
    # TOTAL / DUE
    # ======================================================

    def test_purchase_calculates_total_and_due(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-TOTAL-001",
                quantity="4",
                unit_price="75.00",
                paid_amount="100.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        purchase = Purchase.objects.get(
            invoice_no="PUR-TOTAL-001"
        )

        self.assertEqual(
            purchase.total_amount,
            Decimal("300.00"),
        )

        self.assertEqual(
            purchase.paid_amount,
            Decimal("100.00"),
        )

        self.assertEqual(
            purchase.due_amount,
            Decimal("200.00"),
        )

        self.assertEqual(
            purchase.status,
            "PARTIAL",
        )

    # ======================================================
    # FULLY PAID
    # ======================================================

    def test_fully_paid_purchase_status(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-PAID-001",
                quantity="2",
                unit_price="100.00",
                paid_amount="200.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        purchase = Purchase.objects.get(
            invoice_no="PUR-PAID-001"
        )

        self.assertEqual(
            purchase.total_amount,
            Decimal("200.00"),
        )

        self.assertEqual(
            purchase.paid_amount,
            Decimal("200.00"),
        )

        self.assertEqual(
            purchase.due_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            purchase.status,
            "PAID",
        )

    # ======================================================
    # UNPAID
    # ======================================================

    def test_unpaid_purchase_status(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-UNPAID-001",
                quantity="2",
                unit_price="100.00",
                paid_amount="0.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        purchase = Purchase.objects.get(
            invoice_no="PUR-UNPAID-001"
        )

        self.assertEqual(
            purchase.total_amount,
            Decimal("200.00"),
        )

        self.assertEqual(
            purchase.paid_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            purchase.due_amount,
            Decimal("200.00"),
        )

        self.assertEqual(
            purchase.status,
            "UNPAID",
        )

    # ======================================================
    # CASHBOOK
    # ======================================================

    def test_only_paid_amount_goes_to_cashbook(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-CASH-001",
                quantity="4",
                unit_price="100.00",
                paid_amount="150.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        entries = CashbookEntry.objects.filter(
            entry_type="OUT",
            source_type="PURCHASE",
            reference="PUR-CASH-001",
        )

        self.assertEqual(
            entries.count(),
            1,
        )

        entry = entries.first()

        self.assertEqual(
            entry.amount,
            Decimal("150.00"),
        )

        self.assertEqual(
            entry.reference,
            "PUR-CASH-001",
        )

        self.assertEqual(
            entry.description,
            "Purchase Invoice PUR-CASH-001",
        )

    def test_unpaid_purchase_does_not_create_cashbook_entry(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-NO-CASH-001",
                quantity="2",
                unit_price="100.00",
                paid_amount="0.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertFalse(
            CashbookEntry.objects.filter(
                source_type="PURCHASE",
                reference="PUR-NO-CASH-001",
            ).exists()
        )

    # ======================================================
    # DETAIL
    # ======================================================

    def test_purchase_detail(self):

        self.authenticate(self.admin)

        purchase = Purchase.objects.create(
            supplier=self.supplier,
            invoice_no="PUR-DETAIL-001",
            date="2026-08-26",
            paid_amount=Decimal("0.00"),
        )

        response = self.client.get(
            self.purchase_detail_url(
                purchase.id
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["invoice_no"],
            "PUR-DETAIL-001",
        )

    # ======================================================
    # INVALID PRODUCT
    # ======================================================

    def test_invalid_product_is_rejected(self):

        self.authenticate(self.admin)

        payload = self.purchase_payload(
            invoice_no="PUR-INVALID-PRODUCT-001"
        )

        payload["items"][0]["product_id"] = 999999

        response = self.client.post(
            self.purchase_list_url(),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "does not exist",
            response.data["error"],
        )

        self.assertFalse(
            Purchase.objects.filter(
                invoice_no="PUR-INVALID-PRODUCT-001"
            ).exists()
        )

    # ======================================================
    # ZERO QUANTITY
    # ======================================================

    def test_zero_quantity_is_rejected(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-ZERO-QTY-001",
                quantity="0",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ======================================================
    # NEGATIVE QUANTITY
    # ======================================================

    def test_negative_quantity_is_rejected(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-NEGATIVE-QTY-001",
                quantity="-2",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ======================================================
    # NEGATIVE PAID AMOUNT
    # ======================================================

    def test_negative_paid_amount_is_rejected(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-NEGATIVE-PAYMENT-001",
                paid_amount="-10.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ======================================================
    # PAID > TOTAL
    # ======================================================

    def test_paid_amount_cannot_exceed_total(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-OVERPAY-001",
                quantity="2",
                unit_price="100.00",
                paid_amount="300.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Purchase.objects.filter(
                invoice_no="PUR-OVERPAY-001"
            ).exists()
        )

    # ======================================================
    # MISSING SUPPLIER
    # ======================================================

    def test_missing_supplier_is_rejected(self):

        self.authenticate(self.admin)

        payload = self.purchase_payload(
            invoice_no="PUR-NO-SUPPLIER-001"
        )

        payload.pop("supplier_id")

        response = self.client.post(
            self.purchase_list_url(),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ======================================================
    # MISSING ITEMS
    # ======================================================

    def test_missing_items_is_rejected(self):

        self.authenticate(self.admin)

        payload = self.purchase_payload(
            invoice_no="PUR-NO-ITEMS-001"
        )

        payload["items"] = []

        response = self.client.post(
            self.purchase_list_url(),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ======================================================
    # DUPLICATE INVOICE
    # ======================================================

    def test_duplicate_invoice_number_is_rejected(self):

        self.authenticate(self.admin)

        first_response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-DUPLICATE-001"
            ),
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        second_response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-DUPLICATE-001"
            ),
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ======================================================
    # INVALID UNIT PRICE
    # ======================================================

    def test_negative_unit_price_is_rejected(self):

        self.authenticate(self.admin)

        response = self.client.post(
            self.purchase_list_url(),
            self.purchase_payload(
                invoice_no="PUR-NEGATIVE-PRICE-001",
                unit_price="-10.00",
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
