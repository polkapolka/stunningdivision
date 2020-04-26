from django.test import TestCase, SimpleTestCase
from django.urls import reverse


class LoginViewTest(TestCase):
    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')


class LogoutViewTest(TestCase):
    def test_logout_view_get(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/logout.html')


class AccountViewTest(TestCase):
    def test_account_view_get(self):
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/account.html')


class HomeViewTest(TestCase):
    def test_home_view_get(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')