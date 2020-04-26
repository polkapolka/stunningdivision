import zipcodes
from django.db import models
from django.utils.translation import gettext_lazy as _


class Address(models.Model):
    line_one = models.CharField(
        _('Address Line 1'),
        max_length=1024,
    )

    line_two = models.CharField(
        _('Address Line 2'),
        max_length=1024,
        blank=True,
    )

    city = models.CharField(_('City'),
        max_length=1024,
        blank=True,
    )

    region_state = models.CharField(
        _('State'),
        max_length=1024,
        blank=True,
    )

    code = models.CharField(
        _('Zipcode'),
        max_length=1024,
        blank=True,
    )

    def __str__(self):
        return f"{self.line_one + ','}" \
            f"{self.line_two + ',' if self.line_two else ''}" \
            f"{self.city + ',' if self.city else ''}" \
            f"{self.code + ',' if self.code else ''}"

    class Meta:
        verbose_name_plural = _("Addresses")


class TestingSite(models.Model):
    phone = models.CharField(
        _("Phone Number"),
        max_length=1024,
    )
    address = models.ForeignKey(
        Address,
        verbose_name=_('Address'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(
        _("Testing Site Name"),
        max_length=1024
    )


def is_valid_zip_code(zip_code):
    try:
        return zipcodes.is_real(zip_code)
    except Exception:
        return False

YES_VALUES = {"yes", "y", "1"}
NO_VALUES = {"no", "n", "2"}
def parse_yes_no(text):
    clean_text = text.lower().strip()
    if clean_text in YES_VALUES:
        return True
    if clean_text in NO_VALUES:
        return False
    return None

MILD_VALUES = {"mild", "1"}
SEVERE_VALUES = {"severe", "worsening", "2"}
def parse_symptom_severity(text):
    clean_text = text.lower().strip()
    if clean_text in MILD_VALUES:
        return False
    if clean_text in SEVERE_VALUES:
        return True
    return None



# TODO: Implement
class FakeTestingSite(object):
    def __init__(self, zip_code):
        self.zip_code = zip_code

    def as_text(self):
        return f"123 Testing Drive\nVillageville, State {self.zip_code}"


class UserQuestionnaire(models.Model):
    user_id = models.CharField(_("User identifier"), max_length=1024, primary_key=True)

    wants_questionnaire = models.BooleanField(default=None, null=True)
    can_get_provider_test = models.BooleanField(default=None, null=True)
    is_experiencing_symptoms = models.BooleanField(default=None, null=True)
    has_severe_worsening_symptoms = models.BooleanField(default=None, null=True)

    zip_code = models.CharField(max_length=6, default=None, null=True)

    last_message_sent = models.CharField(max_length=1024, default=None, null=True)

    def process_response(self, current_text):
        if self.wants_questionnaire is None:
            self.wants_questionnaire = parse_yes_no(current_text)
            return

        if self.can_get_provider_test is None:
            self.can_get_provider_test = parse_yes_no(current_text)
            return

        if self.is_experiencing_symptoms is None:
            self.is_experiencing_symptoms = parse_yes_no(current_text)
            return

        if self.has_severe_worsening_symptoms is None:
            self.has_severe_worsening_symptoms = parse_symptom_severity(current_text)

        if self.zip_code is None:
            if is_valid_zip_code(current_text):
                self.zip_code = current_text
            return

    def get_closest_testing_site(self):
        if self.zip_code is None:
            raise ValueError("zip code is not set. Cannot find closest testing site")
        return FakeTestingSite(self.zip_code)


