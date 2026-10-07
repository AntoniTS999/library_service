from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book

User = get_user_model()


class BookViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass123")
        self.staff = User.objects.create_user(
            email="staff@test.com", password="pass123", is_staff=True
        )
        self.book = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            cover="soft",
            inventory=3,
            daily_fee=2.50,
        )

    def test_list_books(self):
        url = reverse("book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_book(self):
        url = reverse("book-detail", args=[self.book.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Dune")

    def test_create_book_requires_staff(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("book-list")
        payload = {"title": "New", "author": "X", "inventory": 1, "daily_fee": 1.0}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_as_staff(self):
        self.client.force_authenticate(user=self.staff)
        url = reverse("book-list")
        payload = {
            "title": "New",
            "author": "test",
            "cover": "soft",
            "inventory": 1,
            "daily_fee": 1.0,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_book_requires_staff(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("book-detail", args=[self.book.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
