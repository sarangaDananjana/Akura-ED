from django.test import TestCase
from django.contrib.auth import get_user_model
from users.serializers import UserCreateSerializer

User = get_user_model()

class UserCreateSerializerTest(TestCase):
    def test_create_user_with_first_name(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test User'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test User')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertIsNotNone(user.auth_version)

