from datetime import date, timedelta

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()


class PaymentModelTests(APITestCase):
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

    def test_payment_creation(self):
        payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/fake",
            session_id="cs_test_fake",
            money_to_pay=20.00,
        )
        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)
        self.assertEqual(payment.borrowing, self.borrowing)

    def test_payment_default_status_is_pending(self):
        payment = Payment.objects.create(
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/fake",
            session_id="cs_test_fake",
            money_to_pay=20.00,
        )
        self.assertEqual(payment.status, Payment.StatusChoices.PENDING)

    def test_borrowing_related_name_payments(self):
        Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/fake",
            session_id="cs_test_fake",
            money_to_pay=20.00,
        )
        self.assertEqual(self.borrowing.payments.count(), 1)

    def test_payment_deleted_when_borrowing_deleted(self):
        Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/fake",
            session_id="cs_test_fake",
            money_to_pay=20.00,
        )
        self.borrowing.delete()
        self.assertEqual(Payment.objects.count(), 0)
