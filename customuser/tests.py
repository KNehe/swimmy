from django.test import TestCase
from django.db.utils import IntegrityError

from .models import User


class CustomUserModelTests(TestCase):
    """Tests for the custom user model"""

    def test_create_user(self):
        """
        Should create a user with user name and password
        Other fields should be empty strings
        """
        user = User.objects.create(email='nehe@gmail.com',
                                   password='123Deaally@')
        self.assertEqual(user.email, 'nehe@gmail.com')
        self.assertEqual(user.password, '123Deaally@')
        self.assertEqual(user.username, '')
        self.assertEqual(user.last_name, '')
        self.assertEqual(type(user.username), str)
        self.assertEqual(type(user.last_name), str)

    def test_do_not_create_user(self):
        """
        Should not create a user when email and password are missing
        Email and password are required fields
        """
        with self.assertRaises(IntegrityError):
            User.objects.create(email=None,
                                last_name='123Deaally@',
                                password=None
                                )

    def test_ensure_unique_fields(self):
        """
        Email should be unique
        """
        with self.assertRaises(IntegrityError):
            User.objects.create(email='nehe@gmail.com',
                                password='123Deaally@')
            User.objects.create(email='nehe@gmail.com',
                                password='123Deaally@')
