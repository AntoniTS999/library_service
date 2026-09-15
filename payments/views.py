from django.db import models
from rest_framework.viewsets import ModelViewSet

from payments.serializers import PaymentSerializer


class PaymentViewSeT(ModelViewSet):
    queryset = models.Payment.objects.all()
    serializer_class = PaymentSerializer
