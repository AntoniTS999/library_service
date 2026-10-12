import stripe
from django.urls import reverse
from payments.models import Payment

FINE_MULTIPLIER = 2


def create_stripe_session(borrowing, request):

    total_price = _calculate_total_price(borrowing)

    session = _create_checkout_session(borrowing, request, total_price)

    return Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price,
    )


def create_fine_session(borrowing, request):

    fine_amount = _calculate_fine(borrowing)

    session = _create_checkout_session(
        borrowing,
        request,
        fine_amount,
        product_name=f"Overdue fine - Borrowing #{borrowing.id} - {borrowing.book.title}",
    )

    return Payment.objects.create(
        status=Payment.StatusChoices.PENDING,
        type=Payment.TypeChoices.FINE,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=fine_amount,
    )


def _create_checkout_session(borrowing, request, amount, product_name=None):
    success_url = (
        request.build_absolute_uri(reverse("payment-success"))
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = request.build_absolute_uri(reverse("payment-cancel"))

    if product_name is None:
        product_name = f"Borrowing #{borrowing.id} - {borrowing.book.title}"

    return stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": product_name,
                    },
                    "unit_amount": _to_cents(amount),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )


def _calculate_total_price(borrowing):
    days = (borrowing.expected_return_date - borrowing.borrow_date).days
    days = max(days, 1)
    return borrowing.book.daily_fee * days


def _calculate_fine(borrowing):
    overdue_days = (borrowing.actual_return_date - borrowing.expected_return_date).days
    return borrowing.book.daily_fee * overdue_days * FINE_MULTIPLIER


def _to_cents(amount):
    return int(amount * 100)
