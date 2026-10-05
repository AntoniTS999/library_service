import stripe
from django.urls import reverse
from payments.models import Payment


def create_stripe_session(borrowing, request):

    total_price = _calculate_total_price(borrowing)

    success_url = (
        request.build_absolute_uri(reverse("payment-success"))
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = request.build_absolute_uri(reverse("payment-cancel"))

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
        success_url=success_url,
        cancel_url=cancel_url,
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
