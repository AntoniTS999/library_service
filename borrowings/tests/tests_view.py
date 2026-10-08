from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


def mock_stripe_session():
    session = MagicMock()
    session.id = "cs_test_fake"
    session.url = "https://checkout.stripe.com/fake"
    return session


class BorrowingCreateViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass123")
        self.book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            cover="soft",
            inventory=2,
            daily_fee=4.00,
        )
        self.client.force_authenticate(user=self.user)

    @patch("payments.helper.stripe.checkout.Session.create")
    def test_create_borrowing_success(self, mock_create):
        """Test if creating a borrowing is working correctly"""

        mock_create.return_value = mock_stripe_session()

        url = reverse("borrowing-list")
        payload = {
            "book": self.book.id,
            "expected_return_date": (date.today() + timedelta(days=7)).isoformat(),
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

    def test_create_borrowing_out_of_stock(self):
        """Test if borrowing impossible when book is out of stock"""

        self.book.inventory = 0
        self.book.save()

        url = reverse("borrowing-list")
        payload = {
            "book": self.book.id,
            "expected_return_date": (date.today() + timedelta(days=7)).isoformat(),
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_borrowing_unauthenticated(self):
        """Test if creating a borrowing with an unauthenticated user fails"""
        self.client.force_authenticate(user=None)
        url = reverse("borrowing-list")
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BorrowingReturnViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass123")
        self.book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            cover="hard",
            inventory=2,
            daily_fee=4.00,
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=date.today() + timedelta(days=5),
        )
        Borrowing.objects.filter(pk=self.borrowing.pk).update(
            borrow_date=date.today() - timedelta(days=10),
            expected_return_date=date.today() - timedelta(days=3),
        )
        self.borrowing.refresh_from_db()
        self.client.force_authenticate(user=self.user)

    def test_return_borrowing_success(self):
        """Test if returning a borrowing is working correctly"""

        url = reverse("borrowing-return-borrowing", args=[self.borrowing.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 3)

    def test_cannot_return_twice(self):
        """Test if it is impossible to return the book twice"""

        url = reverse("borrowing-return-borrowing", args=[self.borrowing.id])
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("payments.helper.stripe.checkout.Session.create")
    def test_overdue_return_creates_fine(self, mock_create):
        """Test if overdue provide to fine"""

        mock_create.return_value = mock_stripe_session()

        url = reverse("borrowing-return-borrowing", args=[self.borrowing.id])
        self.client.post(url)

        self.assertTrue(
            Payment.objects.filter(
                borrowing=self.borrowing, type=Payment.TypeChoices.FINE
            ).exists()
        )


class BorrowingPermissionTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="u1@test.com", password="pass123")
        self.user2 = User.objects.create_user(email="u2@test.com", password="pass123")
        self.staff = User.objects.create_user(
            email="staff@test.com", password="pass123", is_staff=True
        )
        self.book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            cover="hard",
            inventory=5,
            daily_fee=2.00,
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user1,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=7),
        )

    def test_user_sees_only_own_borrowings(self):
        """Tests if user could see only own borrowings"""

        self.client.force_authenticate(user=self.user2)
        url = reverse("borrowing-list")
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)

    def test_staff_sees_all_borrowings(self):
        """Test if admin could see all borrowings"""

        self.client.force_authenticate(user=self.staff)
        url = reverse("borrowing-list")
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
