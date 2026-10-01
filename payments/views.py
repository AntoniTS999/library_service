from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from payments.models import Payment
from payments.serializers import PaymentSerializer


class PaymentViewSeT(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.select_related("borrowing", "borrowing__user")

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)
