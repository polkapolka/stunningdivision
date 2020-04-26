from django.test import TestCase
from django.test import Client
import xml.etree.ElementTree as ET

# Create your tests here.
from core.models import UserQuestionnaire


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
        response = self.client.post("/en-us/home/sms", {"Body": text, "From": self.phone_number})
        self.assertEqual(response.status_code, 200)
        root = ET.fromstring(response.content.decode())
        return root[0].text

    def test_restart(self):
        self.make_sms_request("hello")
        self.make_sms_request("Y")

        user_questionnaire = self.get_user_questionnaire()
        self.assertTrue(user_questionnaire.wants_questionnaire)

        self.make_sms_request("RESTART")
        user_questionnaire.refresh_from_db()
        self.assertEqual(user_questionnaire.wants_questionnaire, None)

    def test_questionnaire_e2e(self):
        self.assertEqual(
            self.make_sms_request("hello"),
            "Welcome to the questionnaire. Would you like to proceed? (Y/N)"
        )
        user_questionnaire = self.get_user_questionnaire()
        self.assertNotEqual(user_questionnaire, None)

        self.assertEqual(
            self.make_sms_request("Y"),
            "Are you experiencing symptoms? (Y/N)"
        )
        user_questionnaire.refresh_from_db()
        self.assertTrue(user_questionnaire.wants_questionnaire)

        self.assertEqual(
            self.make_sms_request("Y"),
            "Are you high risk? (Y/N)"
        )
        user_questionnaire.refresh_from_db()
        self.assertTrue(user_questionnaire.is_experiencing_symptoms)

        self.assertEqual(
            self.make_sms_request("Y"),
            "Are your symptoms 1. Mild 2. Severe 3. Worsening?"
        )
        user_questionnaire.refresh_from_db()
        self.assertTrue(user_questionnaire.is_high_risk)

        self.assertEqual(
            self.make_sms_request("Severe"),
            "What is you preferred testing site type? 1. Walk up 2. Drive through"
        )
        user_questionnaire.refresh_from_db()
        self.assertTrue(user_questionnaire.has_severe_worsening_symptoms)

        self.assertEqual(
            self.make_sms_request("Drive through"),
            "What is your zip code?"
        )
        user_questionnaire.refresh_from_db()
        self.assertEqual(user_questionnaire.preferred_testing_site_type, UserQuestionnaire.TestingSiteTypes.DRIVE_THROUGH)

        self.assertEqual(
            self.make_sms_request("123456"),
            "DT:\n123 Testing Drive\nVillageville, State 123456"
        )
        user_questionnaire.refresh_from_db()
        self.assertEqual(user_questionnaire.zip_code, "123456")

