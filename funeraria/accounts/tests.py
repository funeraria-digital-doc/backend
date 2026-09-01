from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User


class LoginViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='joana',
            email='joana@example.com',
            password='senha12345'
        )

    def test_login_with_correct_credentials(self):
        response = self.client.post('/accounts/login/', {
            'email': 'joana@example.com',
            'password': 'senha12345'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_with_wrong_password(self):
        response = self.client.post('/accounts/login/', {
            'email': 'joana@example.com',
            'password': 'senha-errada'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserModelTests(TestCase):

    def test_str_returns_username(self):
        user = User.objects.create_user(
            username='pedro',
            email='pedro@example.com',
            password='outrasenha'
        )
        self.assertEqual(str(user), 'pedro')
