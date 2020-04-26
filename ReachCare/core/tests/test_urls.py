from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core import views


class TestUrls(SimpleTestCase):

    def test_url_home(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, views.home_view)

    def test_url_login(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, views.login_view)

    def test_url_logout(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, views.logout_view)

    def test_url_account(self):
        url = reverse('account')
        self.assertEqual(resolve(url).func, views.account_view)