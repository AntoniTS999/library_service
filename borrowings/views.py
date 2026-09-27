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
        queryset = self.queryset
        is_active_filter = self.request.query_params.get("is_active")
        if is_active_filter:
            queryset = queryset.filter(actual_return_date__isnull=True)
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBorrowingSerializer
        else:
            return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
