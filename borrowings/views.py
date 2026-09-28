from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, CreateBorrowingSerializer


class BorrowingViewSet(
    GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin
):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.all().select_related("book", "user")
        is_active_filter = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")
        if is_active_filter and is_active_filter.lower() in ("true", "1"):
            queryset = queryset.filter(actual_return_date__isnull=True)
        if self.request.user.is_staff:
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            return queryset
        return queryset.filter(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        with transaction.atomic():
            updated = Borrowing.objects.filter(
                pk=borrowing.pk, actual_return_date__isnull=True
            ).update(actual_return_date=timezone.localdate())

            if not updated:
                return Response(
                    {"detail": "This borrowing has already been returned."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Book.objects.filter(pk=borrowing.book_id).update(
                inventory=F("inventory") + 1
            )

        borrowing.refresh_from_db()
        return Response(self.get_serializer(borrowing).data)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBorrowingSerializer
        else:
            return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
