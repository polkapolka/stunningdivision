import xml.etree.ElementTree as ET

from django.test import Client, TestCase
from django.urls import reverse

from core.models import UserQuestionnaire


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


class TestQuestionnaireView(TestCase):
    def setUp(self):
        self.client = Client()
        self.phone_number = "+1234567890"

    def get_user_questionnaire(self):
        try:
            return UserQuestionnaire.objects.get(user_id=self.phone_number)
        except UserQuestionnaire.DoesNotExist:
            return None

    def make_sms_request(self, text):
        response = self.client.post("/home/sms", {"Body": text, "From": self.phone_number})
        self.assertEqual(response.status_code, 200)
        root = ET.fromstring(response.content.decode())
        return [message.text for message in root]

    def test_restart(self):
        self.make_sms_request("hello")
        self.make_sms_request("Y")

        user_questionnaire = self.get_user_questionnaire()
        self.assertTrue(user_questionnaire.wants_questionnaire)

        self.make_sms_request("RESTART")
        user_questionnaire.refresh_from_db()
        self.assertEqual(user_questionnaire.wants_questionnaire, None)

    def test_unknown_response(self):
        self.make_sms_request("hello")
        messages = self.make_sms_request("hello again")
        self.assertEqual(
            messages[0],
            "Sorry, I didn't understand that. Please reply with one of the given options."
        )

    def test_questionnaire_e2e(self):
        self.make_sms_request("hello"),
        user_questionnaire = self.get_user_questionnaire()
        self.assertNotEqual(user_questionnaire, None)

        self.make_sms_request("Y"),
        user_questionnaire.refresh_from_db()
        self.assertTrue(user_questionnaire.wants_questionnaire)

        self.make_sms_request("Y"),
        user_questionnaire.refresh_from_db()
        self.assertTrue(user_questionnaire.is_experiencing_symptoms)

        self.make_sms_request("Y"),
        user_questionnaire.refresh_from_db()
        self.assertTrue(user_questionnaire.is_high_risk)

        self.make_sms_request("Severe"),
        user_questionnaire.refresh_from_db()
        self.assertTrue(user_questionnaire.has_severe_worsening_symptoms)

        self.make_sms_request("Drive through"),
        user_questionnaire.refresh_from_db()
        self.assertEqual(
            user_questionnaire.preferred_testing_site_type,
            UserQuestionnaire.TestingSiteTypes.DRIVE_THROUGH
        )

        self.make_sms_request("123456")
        user_questionnaire.refresh_from_db()
        self.assertEqual(user_questionnaire.zip_code, "123456")
