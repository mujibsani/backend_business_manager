from decimal import Decimal
from datetime import date

from django.test import TestCase
from django.core.exceptions import ValidationError

from products.models import Product, Category
from suppliers.models import Supplier
from purchases.models import Purchase, PurchaseItem
from purchase_returns.models import (
    PurchaseReturn,
    PurchaseReturnItem,
)
from purchase_returns.services import create_purchase_return


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

    def test_create_purchase_return(self):

        purchase_return = self.create_return(
            quantity=Decimal("2.00")
        )

        self.assertIsNotNone(purchase_return)

        self.assertEqual(
            purchase_return.total_amount,
            Decimal("200.00")
        )

        self.assertEqual(
            purchase_return.refund_amount,
            Decimal("0.00")
        )

        self.assertEqual(
            purchase_return.supplier,
            self.supplier
        )

        self.assertEqual(
            purchase_return.purchase,
            self.purchase
        )

        self.assertEqual(
            purchase_return.items.count(),
            1
        )

    def test_stock_is_reduced(self):

        initial_stock = self.product.stock

        self.create_return(
            quantity=Decimal("2.00")
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            initial_stock - Decimal("2.00")
        )

    def test_purchase_return_with_refund(self):

        purchase_return = self.create_return(
            quantity=Decimal("2.00"),
            refund_amount=Decimal("200.00"),
        )

        self.assertEqual(
            purchase_return.total_amount,
            Decimal("200.00")
        )

        self.assertEqual(
            purchase_return.refund_amount,
            Decimal("200.00")
        )

    def test_cannot_return_more_than_purchased(self):

        with self.assertRaises((ValidationError, ValueError)):

            self.create_return(
                quantity=Decimal("6.00")
            )

    def test_cannot_return_more_than_current_stock(self):

        self.product.stock = Decimal("1.00")
        self.product.save(update_fields=["stock"])

        with self.assertRaises((ValidationError, ValueError)):

            self.create_return(
                quantity=Decimal("2.00")
            )

    def test_cannot_return_more_than_remaining_quantity(self):

        self.create_return(
            quantity=Decimal("3.00")
        )

        with self.assertRaises((ValidationError, ValueError)):

            self.create_return(
                quantity=Decimal("3.00")
            )

    def test_quantity_must_be_positive(self):

        with self.assertRaises((ValidationError, ValueError)):

            self.create_return(
                quantity=Decimal("0.00")
            )

    def test_negative_quantity_is_rejected(self):

        with self.assertRaises((ValidationError, ValueError)):

            self.create_return(
                quantity=Decimal("-1.00")
            )

    def test_negative_refund_is_rejected(self):

        with self.assertRaises((ValidationError, ValueError)):

            self.create_return(
                quantity=Decimal("2.00"),
                refund_amount=Decimal("-10.00"),
            )

    def test_refund_cannot_exceed_return_amount(self):

        with self.assertRaises((ValidationError, ValueError)):

            self.create_return(
                quantity=Decimal("2.00"),
                refund_amount=Decimal("300.00"),
            )

    def test_product_must_exist_in_purchase(self):

        another_product = Product.objects.create(
            name="Another Product",
            category=self.category,
            cost_price=Decimal("200.00"),
            selling_price=Decimal("300.00"),
            stock=Decimal("10.00"),
            min_stock=Decimal("2.00"),
        )

        with self.assertRaises((ValidationError, ValueError)):

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

    def test_supplier_ledger_entry_created(self):

        self.create_return(
            quantity=Decimal("2.00")
        )

        from ledger.models import LedgerEntry

        entry = LedgerEntry.objects.filter(
            supplier=self.supplier,
            reference_type="PURCHASE_RETURN",
            reference_no__isnull=False,
        ).first()

        self.assertIsNotNone(entry)

        self.assertEqual(
            entry.debit,
            Decimal("200.00")
        )

    def test_return_item_subtotal(self):

        purchase_return = self.create_return(
            quantity=Decimal("2.00")
        )

        item = purchase_return.items.first()

        self.assertEqual(
            item.subtotal,
            Decimal("200.00")
        )