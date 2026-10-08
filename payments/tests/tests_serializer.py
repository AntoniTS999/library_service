from datetime import date, timedelta

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentSerializer

User = get_user_model()


class PaymentSerializerTests(APITestCase):
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

    def test_serializer_contains_expected_fields(self):
        """Test serializer contains expected fields"""

        serializer = PaymentSerializer(instance=self.payment)
        data = serializer.data
        for field in [
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        ]:
            self.assertIn(field, data)

    def test_serializer_status_value(self):
        """Test if status value is correct"""

        serializer = PaymentSerializer(instance=self.payment)
        self.assertEqual(serializer.data["status"], "pending")

    def test_serializer_money_to_pay_value(self):
        """Test if money_to_pay value use correctly"""

        serializer = PaymentSerializer(instance=self.payment)
        self.assertEqual(str(serializer.data["money_to_pay"]), "20.00")
