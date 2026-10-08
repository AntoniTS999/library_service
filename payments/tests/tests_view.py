from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import stripe
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


def mock_stripe_session(payment_status="unpaid"):
    session = MagicMock()
    session.payment_status = payment_status
    return session


class PaymentListViewTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="u1@test.com", password="pass123")
        self.user2 = User.objects.create_user(email="u2@test.com", password="pass123")
        self.staff = User.objects.create_user(
            email="staff@test.com", password="pass123", is_staff=True
        )
        self.book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            cover="soft",
            inventory=3,
            daily_fee=4.00,
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user1,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=5),
        )
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/fake",
            session_id="cs_test_fake",
            money_to_pay=20.00,
        )

    def test_owner_sees_own_payment(self):
        """Test that user could see only own payment"""

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse("payment-list"))
        self.assertEqual(len(response.data), 1)

    def test_other_user_sees_nothing(self):
        """Test if other users couldn't see payment"""

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse("payment-list"))
        self.assertEqual(len(response.data), 0)

    def test_staff_sees_all(self):
        """Test if staff can see all payments"""

        self.client.force_authenticate(user=self.staff)
        response = self.client.get(reverse("payment-list"))
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_rejected(self):
        """Test authentication is needed"""

        response = self.client.get(reverse("payment-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_payment(self):
        """Test payment details return correctly"""

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse("payment-detail", args=[self.payment.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaymentSuccessActionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass123")
        self.book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            cover="hard",
            inventory=3,
            daily_fee=4.00,
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=5),
        )
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/fake",
            session_id="cs_test_fake",
            money_to_pay=20.00,
        )
        self.client.force_authenticate(user=self.user)

    @patch("payments.views.stripe.checkout.Session.retrieve")
    def test_success_marks_paid(self, mock_retrieve):
        """Test successfully made payments marks paid"""

        mock_retrieve.return_value = mock_stripe_session(payment_status="paid")
        url = reverse("payment-success")
        response = self.client.get(url, {"session_id": self.payment.session_id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.StatusChoices.PAID)

    @patch("payments.views.stripe.checkout.Session.retrieve")
    def test_success_unpaid_session(self, mock_retrieve):
        """Test not paid session work properly"""

        mock_retrieve.return_value = mock_stripe_session(payment_status="unpaid")
        url = reverse("payment-success")
        response = self.client.get(url, {"session_id": self.payment.session_id})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.StatusChoices.PENDING)


class PaymentCancelActionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass123")
        self.client.force_authenticate(user=self.user)

    def test_cancel_returns_200_with_message(self):
        """Test cancel works properly"""

        response = self.client.get(reverse("payment-cancel"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("24", response.data["detail"])
