from rest_framework.viewsets import ModelViewSet

from payments.models import Payment
from payments.serializers import PaymentSerializer


class PaymentViewSeT(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
