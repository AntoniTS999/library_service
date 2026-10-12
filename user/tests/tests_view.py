from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegistrationViewTests(APITestCase):
    def test_register_new_user(self):
        """Test crete endpoint work correctly"""

        url = reverse("user:create")
        payload = {"email": "new@test.com", "password": "pass123"}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@test.com").exists())

    def test_register_duplicate_email_fails(self):
        """Test if user should have unique email"""

        User.objects.create_user(email="dup@test.com", password="pass123")
        url = reverse("user:create")
        payload = {"email": "dup@test.com", "password": "pass456"}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserMeViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass123")

    def test_get_own_profile_authenticated(self):
        """Test if authenticated user can see own profile"""

        self.client.force_authenticate(user=self.user)
        url = reverse("user:manage-user")  # adjust to your actual URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user@test.com")

    def test_get_profile_unauthenticated(self):
        """Test if unauthenticated user forbidden"""

        url = reverse("user:manage-user")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenObtainViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="pass123")

    def test_obtain_token_with_valid_credentials(self):
        """Test if token works correctly"""

        url = reverse("user:token_obtain_pair")  # standard simplejwt URL name
        response = self.client.post(
            url, {"email": "user@test.com", "password": "pass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_obtain_token_with_invalid_credentials(self):
        """Test if access with invalid credentials fails"""

        url = reverse("user:token_obtain_pair")
        response = self.client.post(
            url, {"email": "user@test.com", "password": "wrong"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
