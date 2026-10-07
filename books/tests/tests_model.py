from rest_framework.test import APITestCase

from books.models import Book


class ModelTest(APITestCase):

    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="hard",
            inventory=5,
            daily_fee=10,
        )

    def test_book_str(self):
        """Test check if model str return data correctly"""
        self.assertEqual(
            str(self.book),
            f"{self.book.title} by {self.book.author} in {self.book.cover} cover: {self.book.inventory} left",
        )

    def test_inventory_can_be_zero(self):
        """Test check if inventory can't be zero"""
        self.book.inventory = 0
        self.book.save()
        self.assertEqual(self.book.inventory, 0)
