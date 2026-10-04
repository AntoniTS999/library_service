from django.db import transaction
from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from borrowings.models import Borrowing
from payments.helper import create_stripe_session
from payments.serializers import PaymentSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
            "payments",
        ]
        read_only_fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]


class CreateBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["book", "expected_return_date"]

    def validate_book(self, value):
        if value.inventory <= 0:
            raise serializers.ValidationError("Inventory must be greater than 0")
        return value

    def create(self, validated_data):
        book = validated_data["book"]

        with transaction.atomic():
            updated = Book.objects.filter(id=book.id, inventory__gt=0).update(
                inventory=F("inventory") - 1
            )

            if not updated:
                raise ValidationError({"book": "Inventory must be greater than 0"})

            borrowing = Borrowing.objects.create(**validated_data)
            create_stripe_session(borrowing)

        return borrowing
