from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, CreateBorrowingSerializer


class BorrowingViewSet(
    GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin
):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Borrowing.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBorrowingSerializer
        else:
            return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
