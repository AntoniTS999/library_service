import stripe
import os
import dotenv

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

session = stripe.checkout.Session.create(
    line_items=[
        {
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Library fine - test book"},
                "unit_amount": 2000,  # kwota w centach -> 20.00 USD
            },
            "quantity": 1,
        }
    ],
    mode="payment",
    success_url="http://localhost:8000/payments/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url="http://localhost:8000/payments/cancel",
)

print("session.id:", session.id)
print("session.url:", session.url)
