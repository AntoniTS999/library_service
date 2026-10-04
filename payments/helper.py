import stripe
from django.conf import settings

from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

DEFAULT_SUCCESS_URL = "http://localhost:8000/payments/success/"
DEFAULT_CANCEL_URL = "http://localhost:8000/payments/cancel/"


def create_stripe_session(borrowing):

    total_price = _calculate_total_price(borrowing)

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Borrowing #{borrowing.id} - {borrowing.book.title}",
                    },
                    "unit_amount": _to_cents(total_price),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=DEFAULT_SUCCESS_URL,
        cancel_url=DEFAULT_CANCEL_URL,
    )

    return Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price,
    )


def _calculate_total_price(borrowing):
    days = (borrowing.expected_return_date - borrowing.borrow_date).days
    days = max(days, 1)
    return borrowing.book.daily_fee * days


def _to_cents(amount):
    return int(amount * 100)
