from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class UserModelTests(APITestCase):
    def test_create_user(self):
        """Test creating a new user is correct"""

        user = User.objects.create_user(email="user@test.com", password="pass123")
        self.assertEqual(user.email, "user@test.com")
        self.assertTrue(user.check_password("pass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a new superuser is correct"""

        admin = User.objects.create_superuser(
            email="admin@test.com", password="pass123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_str_representation(self):
        """Test that the user string representation is correct"""

        user = User.objects.create_user(email="user@test.com", password="pass123")
        self.assertEqual(str(user), "user@test.com")
