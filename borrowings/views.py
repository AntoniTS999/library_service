from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer


class BorrowingViewSet(
    GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
