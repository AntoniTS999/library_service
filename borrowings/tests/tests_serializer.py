from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.serializers import BorrowingSerializer, CreateBorrowingSerializer
from payments.models import Payment

User = get_user_model()


def mock_stripe_session():
    session = MagicMock()
    session.id = "cs_test_fake"
    session.url = "https://checkout.stripe.com/fake"
    return session


def fake_request():
    return type(
        "Request",
        (),
        {"build_absolute_uri": lambda self, path: f"http://testserver{path}"},
    )()


class CreateBorrowingSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass123")
        self.book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            cover="hard",
            inventory=2,
            daily_fee=4.00,
        )

    def test_validate_book_rejects_zero_inventory(self):
        """Test if it is impossible to borrow book when inventory is zero"""

        self.book.inventory = 0
        self.book.save()
        serializer = CreateBorrowingSerializer(
            data={
                "book": self.book.id,
                "expected_return_date": date.today() + timedelta(days=5),
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("book", serializer.errors)

    def test_validate_book_accepts_positive_inventory(self):
        """Test if it is possible to borrow book when inventory is positive"""
        serializer = CreateBorrowingSerializer(
            data={
                "book": self.book.id,
                "expected_return_date": date.today() + timedelta(days=5),
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    @patch("payments.helper.stripe.checkout.Session.create")
    def test_create_decreases_inventory_and_creates_payment(self, mock_create):
        """Test if inventory decrease when borrow and payment appear for the borrowed book"""

        mock_create.return_value = mock_stripe_session()

        serializer = CreateBorrowingSerializer(
            data={
                "book": self.book.id,
                "expected_return_date": date.today() + timedelta(days=5),
            },
            context={"request": fake_request()},
        )
        serializer.is_valid(raise_exception=True)
        borrowing = serializer.save(user=self.user)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)
        self.assertEqual(Payment.objects.filter(borrowing=borrowing).count(), 1)
