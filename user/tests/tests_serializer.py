from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from user.serializers import UserSerializer

User = get_user_model()


class UserSerializerTests(APITestCase):
    def test_create_user_via_serializer(self):
        """Test if user serializer works correctly"""

        payload = {"email": "new@test.com", "password": "pass123"}
        serializer = UserSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertTrue(user.check_password("pass123"))

    def test_serializer_rejects_duplicate_email(self):
        """Test if serializer rejects duplicate email"""

        User.objects.create_user(email="dup@test.com", password="pass123")
        serializer = UserSerializer(
            data={"email": "dup@test.com", "password": "pass123"}
        )
        self.assertFalse(serializer.is_valid())
