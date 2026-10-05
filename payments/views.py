from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from payments.models import Payment
from payments.serializers import PaymentSerializer

import stripe
from django.conf import settings
from rest_framework.decorators import action

stripe.api_key = settings.STRIPE_API_KEY


class PaymentViewSeT(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.select_related("borrowing", "borrowing__user")

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)

    @action(detail=False, methods=["get"], url_path="success")
    def success(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"detail": "Missing session_id."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError:
            return Response(
                {"detail": "Invalid session_id."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.get(session_id=session_id)
        except Payment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if session.payment_status == "paid":
            payment.status = Payment.StatusChoices.PAID
            payment.save()
            return Response(
                {"detail": "Payment was successful. Thank you!"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Payment was not completed yet."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], url_path="cancel")
    def cancel(self, request):
        return Response(
            {
                "detail": "Payment was not completed. You can pay later, but the payment session is available for only 24 hours."
            },
            status=status.HTTP_200_OK,
        )
