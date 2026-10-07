from django.utils import timezone
from datetime import date, timedelta

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from books.models import Book
from borrowings.models import Borrowing

User = get_user_model()


class ModelTest(APITestCase):
    """Test check if models str return data correctly"""

    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="hard",
            inventory=5,
            daily_fee=10,
        )
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="123456789",
        )

    def test_borrowing_str(self):
        """Check if borrowing str return correct data"""
        self.borrowings = Borrowing.objects.create(
            borrow_date=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=1),
            book=self.book,
            user=self.user,
        )
        self.assertEqual(
            str(self.borrowings),
            f"User: {self.borrowings.user.id} borrowed book: {self.borrowings.book.id} for period from: {self.borrowings.borrow_date} to: {self.borrowings.expected_return_date}",
        )

    def test_borrowing_creation(self):
        """Check if borrowing creation return correct data"""

        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=7),
        )
        self.assertIsNone(borrowing.actual_return_date)
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)

    def test_is_active_true_when_not_returned(self):
        """Check if borrowing is active when not returning data"""

        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=7),
        )
        self.assertTrue(borrowing.is_active)

    def test_is_active_false_when_returned(self):
        """Check if borrowing is not active when returned data"""

        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=7),
            actual_return_date=date.today(),
        )
        self.assertFalse(borrowing.is_active)
