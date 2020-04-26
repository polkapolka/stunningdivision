from django.test import TestCase
from django.test import Client
import xml.etree.ElementTree as ET

# Create your tests here.


class TestQuestionnaireView(TestCase):
    def setUp(self):
        self.client = Client()
        self.phone_number = "+1234567890"

    def make_sms_request(self, text):
        response = self.client.post("/en-us/home/sms", {"Body": text, "From": self.phone_number})
        self.assertEqual(response.status_code, 200)
        root = ET.fromstring(response.content.decode())
        return root[0].text

    def test_questionnaire_e2e(self):
        self.assertEqual(
            self.make_sms_request("hello"),
            "Welcome to the questionnaire. Would you like to proceed? (Y/N)"
        )

        self.assertEqual(
            self.make_sms_request("Y"),
            "Are you experiencing symptoms? (Y/N)"
        )

        self.assertEqual(
            self.make_sms_request("Y"),
            "Are you high risk? (Y/N)"
        )

        self.assertEqual(
            self.make_sms_request("Y"),
            "Are your symptoms 1. Mild 2. Severe 3. Worsening?"
        )

        self.assertEqual(
            self.make_sms_request("Severe"),
            "What is you preferred testing site type? 1. Walk up 2. Drive through"
        )

        self.assertEqual(
            self.make_sms_request("Drive through"),
            "What is your zip code?"
        )

        self.assertEqual(
            self.make_sms_request("123456"),
            "DT:\n123 Testing Drive\nVillageville, State 123456"
        )

