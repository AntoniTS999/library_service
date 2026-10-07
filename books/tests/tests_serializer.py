from rest_framework.test import APITestCase

from books.models import Book
from books.serializers import BookSerializer


class BookSerializerTests(APITestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            cover="hard",
            inventory=5,
            daily_fee=2.50,
        )

    def test_serializer_contains_expected_fields(self):
        """Check if serializer has expected fields"""

        serializer = BookSerializer(instance=self.book)
        data = serializer.data
        self.assertIn("title", data)
        self.assertIn("author", data)
        self.assertIn("inventory", data)
        self.assertIn("daily_fee", data)

    def test_serializer_valid_data(self):
        """Check if serializer has valid data"""

        payload = {
            "title": "New Book",
            "author": "Someone",
            "inventory": 3,
            "daily_fee": "1.50",
            "cover": "hard",
        }
        serializer = BookSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_rejects_negative_inventory(self):
        """Check if serializer rejects negative inventory"""

        payload = {
            "title": "New Book",
            "author": "Someone",
            "inventory": -1,
            "cover": "hard",
            "daily_fee": "1.50",
        }
        serializer = BookSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
