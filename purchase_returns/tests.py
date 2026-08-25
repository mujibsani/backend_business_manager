from decimal import Decimal
from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from products.models import Product, Category
from suppliers.models import Supplier
from purchases.models import Purchase, PurchaseItem

from purchase_returns.models import (
    PurchaseReturn,
    PurchaseReturnItem,
)

from purchase_returns.services import (
    create_purchase_return,
)


class PurchaseReturnServiceTests(TestCase):

    def setUp(self):

        self.category = Category.objects.create(
            name="Test Category"
        )

        self.supplier = Supplier.objects.create(
            name="Test Supplier"
        )

        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            cost_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock=Decimal("10.00"),
            min_stock=Decimal("2.00"),
        )

        self.purchase = Purchase.objects.create(
            invoice_no="PUR-TEST-001",
            supplier=self.supplier,
            date=date.today(),
            total_amount=Decimal("500.00"),
            paid_amount=Decimal("500.00"),
            due_amount=Decimal("0.00"),
            status="PAID",
        )

        self.purchase_item = PurchaseItem.objects.create(
            purchase=self.purchase,
            product=self.product,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
        )

        self.purchase.update_totals()

    # ======================================================
    # HELPER
    # ======================================================

    def create_return(
        self,
        quantity=Decimal("2.00"),
        refund_amount=Decimal("0.00"),
    ):

        return create_purchase_return(
            purchase=self.purchase,
            supplier=self.supplier,
            date=date.today(),
            items=[
                {
                    "product": self.product,
                    "quantity": quantity,
                    "unit_price": Decimal("100.00"),
                }
            ],
            refund_amount=refund_amount,
        )

    # ======================================================
    # CREATE
    # ======================================================

    def test_create_purchase_return(self):

        purchase_return = self.create_return(
            quantity=Decimal("2.00")
        )

        self.assertIsNotNone(
            purchase_return
        )

        self.assertEqual(
            purchase_return.total_amount,
            Decimal("200.00"),
        )

        self.assertEqual(
            purchase_return.refund_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            purchase_return.supplier,
            self.supplier,
        )

        self.assertEqual(
            purchase_return.purchase,
            self.purchase,
        )

        self.assertEqual(
            purchase_return.items.count(),
            1,
        )

        self.assertEqual(
            purchase_return.status,
            "COMPLETED",
        )

    # ======================================================
    # RETURN NUMBER
    # ======================================================

    def test_return_number_is_generated(self):

        purchase_return = self.create_return()

        self.assertEqual(
            purchase_return.return_no,
            "PR-000001",
        )

    def test_second_return_number_is_sequential(self):

        first = self.create_return(
            quantity=Decimal("1.00")
        )

        second = self.create_return(
            quantity=Decimal("1.00")
        )

        self.assertEqual(
            first.return_no,
            "PR-000001",
        )

        self.assertEqual(
            second.return_no,
            "PR-000002",
        )

    # ======================================================
    # STOCK
    # ======================================================

    def test_stock_is_reduced(self):

        initial_stock = self.product.stock

        self.create_return(
            quantity=Decimal("2.00")
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            initial_stock - Decimal("2.00"),
        )

    # ======================================================
    # REFUND
    # ======================================================

    def test_purchase_return_with_refund(self):

        purchase_return = self.create_return(
            quantity=Decimal("2.00"),
            refund_amount=Decimal("200.00"),
        )

        self.assertEqual(
            purchase_return.total_amount,
            Decimal("200.00"),
        )

        self.assertEqual(
            purchase_return.refund_amount,
            Decimal("200.00"),
        )

    # ======================================================
    # PURCHASE UPDATE
    # ======================================================

    def test_purchase_total_is_reduced(self):

        self.create_return(
            quantity=Decimal("2.00")
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.total_amount,
            Decimal("300.00"),
        )

    def test_purchase_paid_amount_is_reduced_by_refund(self):

        self.create_return(
            quantity=Decimal("2.00"),
            refund_amount=Decimal("200.00"),
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.paid_amount,
            Decimal("300.00"),
        )

    def test_purchase_due_is_recalculated(self):

        self.create_return(
            quantity=Decimal("2.00"),
            refund_amount=Decimal("100.00"),
        )

        self.purchase.refresh_from_db()

        self.assertEqual(
            self.purchase.total_amount,
            Decimal("300.00"),
        )

        self.assertEqual(
            self.purchase.paid_amount,
            Decimal("400.00"),
        )

        self.assertEqual(
            self.purchase.due_amount,
            Decimal("0.00"),
        )

        self.assertEqual(
            self.purchase.status,
            "PAID",
        )

    # ======================================================
    # QUANTITY VALIDATION
    # ======================================================

    def test_cannot_return_more_than_purchased(self):

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            self.create_return(
                quantity=Decimal("6.00")
            )

    def test_cannot_return_more_than_current_stock(self):

        self.product.stock = Decimal("1.00")

        self.product.save(
            update_fields=["stock"]
        )

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            self.create_return(
                quantity=Decimal("2.00")
            )

    def test_cannot_return_more_than_remaining_quantity(self):

        self.create_return(
            quantity=Decimal("3.00")
        )

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            self.create_return(
                quantity=Decimal("3.00")
            )

    def test_quantity_must_be_positive(self):

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            self.create_return(
                quantity=Decimal("0.00")
            )

    def test_negative_quantity_is_rejected(self):

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            self.create_return(
                quantity=Decimal("-1.00")
            )

    # ======================================================
    # REFUND VALIDATION
    # ======================================================

    def test_negative_refund_is_rejected(self):

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            self.create_return(
                quantity=Decimal("2.00"),
                refund_amount=Decimal("-10.00"),
            )

    def test_refund_cannot_exceed_return_amount(self):

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            self.create_return(
                quantity=Decimal("2.00"),
                refund_amount=Decimal("300.00"),
            )

    def test_refund_cannot_exceed_paid_amount(self):

        self.purchase.paid_amount = Decimal("100.00")
        self.purchase.due_amount = Decimal("400.00")
        self.purchase.status = "PARTIAL"

        self.purchase.save(
            update_fields=[
                "paid_amount",
                "due_amount",
                "status",
            ]
        )

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            self.create_return(
                quantity=Decimal("2.00"),
                refund_amount=Decimal("200.00"),
            )

    # ======================================================
    # PRODUCT VALIDATION
    # ======================================================

    def test_product_must_exist_in_purchase(self):

        another_product = Product.objects.create(
            name="Another Product",
            category=self.category,
            cost_price=Decimal("200.00"),
            selling_price=Decimal("300.00"),
            stock=Decimal("10.00"),
            min_stock=Decimal("2.00"),
        )

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            create_purchase_return(
                purchase=self.purchase,
                supplier=self.supplier,
                date=date.today(),
                items=[
                    {
                        "product": another_product,
                        "quantity": Decimal("1.00"),
                        "unit_price": Decimal("200.00"),
                    }
                ],
                refund_amount=Decimal("0.00"),
            )

    def test_duplicate_product_is_rejected(self):

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            create_purchase_return(
                purchase=self.purchase,
                supplier=self.supplier,
                date=date.today(),
                items=[
                    {
                        "product": self.product,
                        "quantity": Decimal("1.00"),
                    },
                    {
                        "product": self.product,
                        "quantity": Decimal("1.00"),
                    },
                ],
                refund_amount=Decimal("0.00"),
            )

    # ======================================================
    # SUPPLIER VALIDATION
    # ======================================================

    def test_supplier_must_match_purchase(self):

        another_supplier = Supplier.objects.create(
            name="Another Supplier",
            phone="01700000002",    
        )

        with self.assertRaises(
            (ValidationError, ValueError)
        ):

            create_purchase_return(
                purchase=self.purchase,
                supplier=another_supplier,
                date=date.today(),
                items=[
                    {
                        "product": self.product,
                        "quantity": Decimal("1.00"),
                    }
                ],
                refund_amount=Decimal("0.00"),
            )

    # ======================================================
    # LEDGER
    # ======================================================

    def test_supplier_ledger_entry_created(self):

        self.create_return(
            quantity=Decimal("2.00")
        )

        from ledger.models import LedgerEntry

        entry = (
            LedgerEntry.objects
            .filter(
                supplier=self.supplier,
                reference_type="PURCHASE_RETURN",
                reference_no__isnull=False,
            )
            .first()
        )

        self.assertIsNotNone(
            entry
        )

        self.assertEqual(
            entry.debit,
            Decimal("200.00"),
        )

    # ======================================================
    # CASHBOOK
    # ======================================================

    def test_cashbook_entry_created_for_refund(self):

        self.create_return(
            quantity=Decimal("2.00"),
            refund_amount=Decimal("200.00"),
        )

        from cashbook.models import CashbookEntry

        entry = (
            CashbookEntry.objects
            .filter(
                entry_type="IN",
                source_type="PURCHASE_RETURN",
                reference__startswith="PR-",
            )
            .first()
        )

        self.assertIsNotNone(
            entry
        )

        self.assertEqual(
            entry.amount,
            Decimal("200.00"),
        )

    def test_no_cashbook_entry_without_refund(self):

        self.create_return(
            quantity=Decimal("2.00"),
            refund_amount=Decimal("0.00"),
        )

        from cashbook.models import CashbookEntry

        entry_count = (
            CashbookEntry.objects
            .filter(
                source_type="PURCHASE_RETURN"
            )
            .count()
        )

        self.assertEqual(
            entry_count,
            0,
        )

    # ======================================================
    # RETURN ITEM
    # ======================================================

    def test_return_item_subtotal(self):

        purchase_return = self.create_return(
            quantity=Decimal("2.00")
        )

        item = purchase_return.items.first()

        self.assertEqual(
            item.quantity,
            Decimal("2.00"),
        )

        self.assertEqual(
            item.unit_price,
            Decimal("100.00"),
        )

        self.assertEqual(
            item.subtotal,
            Decimal("200.00"),
        )

    def test_original_purchase_price_is_used(self):

        purchase_return = self.create_return(
            quantity=Decimal("2.00")
        )

        item = purchase_return.items.first()

        self.assertEqual(
            item.unit_price,
            self.purchase_item.unit_price,
        )

    # ======================================================
    # RETURN HEADER
    # ======================================================

    def test_return_date_is_set(self):

        purchase_return = self.create_return()

        self.assertEqual(
            purchase_return.date,
            date.today(),
        )

    def test_return_status_is_completed(self):

        purchase_return = self.create_return()

        self.assertEqual(
            purchase_return.status,
            "COMPLETED",
        )