from django.utils import timezone
from datetime import timedelta

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from books.models import Book
from borrowings.models import Borrowing


class ModelTestStr(APITestCase):
    """Tests check if models str return data correctly"""

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
        self.borrowings = Borrowing.objects.create(
            borrow_date=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=1),
            book=self.book,
            user=self.user,
        )


    def test_borrowing_str(self):
        self.assertEqual(
            str(self.borrowings),
            f"User: {self.borrowings.user.id} borrowed book: {self.borrowings.book.id} for period from: {self.borrowings.borrow_date} to: {self.borrowings.expected_return_date}",
        )
