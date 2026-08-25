from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from accounts.models import User

from .models import CashbookEntry
from .services import (
_create_cashbook_entry,
cash_in,
cash_out,
get_cashbook_summary,
)

class CashbookServiceTests(TestCase):
    """Test cashbook service functions."""

    def setUp(self):
        self.today = date(2026, 8, 26)

    def test_cash_in_creates_entry(self):
        entry = cash_in(
            amount="1000.00",
            source_type="SALE",
            date=self.today,
            reference="SALE-001",
            description="Cash received from sale",
        )

        self.assertIsNotNone(entry.pk)
        self.assertEqual(entry.entry_type, "IN")
        self.assertEqual(entry.source_type, "SALE")
        self.assertEqual(entry.amount, Decimal("1000.00"))
        self.assertEqual(entry.reference, "SALE-001")
        self.assertEqual(
            entry.description,
            "Cash received from sale",
        )

    def test_cash_out_creates_entry(self):
        entry = cash_out(
            amount="500.00",
            source_type="EXPENSE",
            date=self.today,
            reference="EXP-001",
            description="Office expense",
        )

        self.assertIsNotNone(entry.pk)
        self.assertEqual(entry.entry_type, "OUT")
        self.assertEqual(entry.source_type, "EXPENSE")
        self.assertEqual(entry.amount, Decimal("500.00"))
        self.assertEqual(entry.reference, "EXP-001")
        self.assertEqual(
            entry.description,
            "Office expense",
        )

    def test_cash_in_zero_amount_is_rejected(self):
        with self.assertRaises(ValidationError):
            cash_in(
                amount="0",
                source_type="SALE",
                date=self.today,
            )

    def test_cash_out_zero_amount_is_rejected(self):
        with self.assertRaises(ValidationError):
            cash_out(
                amount="0",
                source_type="EXPENSE",
                date=self.today,
            )

    def test_cash_in_negative_amount_is_rejected(self):
        with self.assertRaises(ValidationError):
            cash_in(
                amount="-100",
                source_type="SALE",
                date=self.today,
            )

    def test_cash_out_negative_amount_is_rejected(self):
        with self.assertRaises(ValidationError):
            cash_out(
                amount="-100",
                source_type="EXPENSE",
                date=self.today,
            )

    def test_invalid_amount_is_rejected(self):
        with self.assertRaises(ValidationError):
            cash_in(
                amount="invalid",
                source_type="SALE",
                date=self.today,
            )

    def test_invalid_entry_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            _create_cashbook_entry(
                entry_type="INVALID",
                source_type="SALE",
                amount="100",
                date=self.today,
            )

    def test_invalid_source_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            _create_cashbook_entry(
                entry_type="IN",
                source_type="INVALID",
                amount="100",
                date=self.today,
            )

    def test_cashbook_summary(self):
        cash_in(
            amount="1000",
            source_type="SALE",
            date=self.today,
        )

        cash_in(
            amount="500",
            source_type="OTHER",
            date=self.today,
        )

        cash_out(
            amount="300",
            source_type="EXPENSE",
            date=self.today,
        )

        cash_out(
            amount="200",
            source_type="PURCHASE",
            date=self.today,
        )

        summary = get_cashbook_summary()

        self.assertEqual(
            summary["cash_in"],
            Decimal("1500"),
        )
        self.assertEqual(
            summary["cash_out"],
            Decimal("500"),
        )
        self.assertEqual(
            summary["balance"],
            Decimal("1000"),
        )

    def test_empty_cashbook_summary(self):
        summary = get_cashbook_summary()

        self.assertEqual(
            summary["cash_in"],
            Decimal("0.00"),
        )
        self.assertEqual(
            summary["cash_out"],
            Decimal("0.00"),
        )
        self.assertEqual(
            summary["balance"],
            Decimal("0.00"),
        )

    def test_multiple_cashbook_entries(self):
        cash_in(
            amount="100",
            source_type="SALE",
            date=self.today,
        )

        cash_in(
            amount="200",
            source_type="SALE",
            date=self.today,
        )

        cash_out(
            amount="50",
            source_type="EXPENSE",
            date=self.today,
        )

        self.assertEqual(
            CashbookEntry.objects.count(),
            3,
        )


class CashbookAPITests(TestCase):
    """Test cashbook API permissions and responses."""


    def setUp(self):
        self.client = APIClient()
        self.url = reverse("cashbook")
        self.today = date(2026, 8, 26)

        self.admin = User.objects.create_user(
            username="cashbook_admin",
            password="TestPassword123",
        )

        self.manager = User.objects.create_user(
            username="cashbook_manager",
            password="TestPassword123",
        )

        self.staff = User.objects.create_user(
            username="cashbook_staff",
            password="TestPassword123",
        )

        self.admin.role = "ADMIN"
        self.admin.save(update_fields=["role"])

        self.manager.role = "MANAGER"
        self.manager.save(update_fields=["role"])

        self.staff.role = "STAFF"
        self.staff.save(update_fields=["role"])

        cash_in(
            amount="1000",
            source_type="SALE",
            date=self.today,
            reference="SALE-001",
            description="Customer payment",
        )

        cash_in(
            amount="500",
            source_type="OTHER",
            date=self.today,
            reference="OTHER-001",
        )

        cash_out(
            amount="300",
            source_type="EXPENSE",
            date=self.today,
            reference="EXP-001",
            description="Office expense",
        )

    def test_unauthenticated_user_cannot_access_cashbook(self):
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            [401, 403],
        )

    def test_admin_can_access_cashbook(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_manager_can_access_cashbook(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_staff_cannot_access_cashbook(self):
        self.client.force_authenticate(
            user=self.staff,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_admin_receives_correct_summary(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["summary"]["cash_in"],
            Decimal("1500"),
        )

        self.assertEqual(
            response.data["summary"]["cash_out"],
            Decimal("300"),
        )

        self.assertEqual(
            response.data["summary"]["balance"],
            Decimal("1200"),
        )

    def test_cashbook_returns_entries(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "entries",
            response.data,
        )

        self.assertEqual(
            len(response.data["entries"]),
            3,
        )

    def test_cashbook_entry_contains_expected_fields(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        entry = response.data["entries"][0]

        expected_fields = {
            "id",
            "date",
            "type",
            "source_type",
            "amount",
            "reference",
            "description",
        }

        self.assertEqual(
            set(entry.keys()),
            expected_fields,
        )

    def test_cashbook_post_is_not_allowed(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.post(
            self.url,
            {
                "entry_type": "IN",
                "source_type": "OTHER",
                "amount": "100",
                "date": self.today,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_cashbook_put_is_not_allowed(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.put(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_cashbook_patch_is_not_allowed(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.patch(
            self.url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_cashbook_delete_is_not_allowed(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_entries_are_ordered_by_date_and_id_descending(self):
        older_date = date(2026, 8, 25)

        older_entry = cash_in(
            amount="50",
            source_type="OTHER",
            date=older_date,
        )

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200,
        )

        entries = response.data["entries"]

        self.assertEqual(
            entries[0]["date"],
            self.today,
        )

        self.assertEqual(
            entries[-1]["id"],
            older_entry.id,
        )

