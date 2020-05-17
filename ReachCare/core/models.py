import zipcodes
from django.db import models
from phone_field import PhoneField
from django.utils.translation import gettext_lazy as _
import requests
import json

ZIP_API_KEY = "PJ7Ha3OkOoK18zRDI37edh6Lwmz5LdNkwCDymlCgNHNWQPuVjE6CMqwypODh1owf"


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
        return f"{self.line_one + ', '}" \
            f"{self.line_two + ', ' if self.line_two else ''}" \
            f"{self.city + ', ' if self.city else ''}" \
            f"{self.region_state + ', ' if self.region_state else ''}" \
            f"{self.code if self.code else ''}"

    class Meta:
        verbose_name_plural = _("Addresses")


class Provider(models.Model):
    provider_name = models.CharField(
        _("Testing Provider Name"),
        max_length=1024
    )
    provider_phone = PhoneField(blank=True, help_text='Contact Provider to schedule test')
    provider_alt_phone = PhoneField(blank=True)

    def __str__(self):
        return f"{self.provider_name}"

class TestingSite(models.Model):
    provider = models.ForeignKey(Provider,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 )

    address = models.ForeignKey(
        Address,
        verbose_name=_('Address'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    site_name = models.CharField(
        _("Testing Site Name"),
        max_length=1024
    )
    site_phone = PhoneField(blank=True, help_text='Contact Provider to schedule test')

    def as_text(self):
        testing_site_text = f"Your closest testing site is\n{self.site_name}\n{self.address}\n\nCall this number:\n{self.provider.provider_phone}\n to schedule a test."
        return testing_site_text


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


MILD_VALUES = {"mild", "moderate", "1"}
SEVERE_VALUES = {"severe", "worsening", "2"}


def parse_symptom_severity(text):
    clean_text = text.lower().strip()
    if clean_text in MILD_VALUES:
        return False
    if clean_text in SEVERE_VALUES:
        return True
    return None


def in_philadelphia(zipcode):
    url = f"https://www.zipcodeapi.com/rest/{ZIP_API_KEY}/city-zips.json/Philadelphia/PA"
    response = requests.get(url)
    philadelphia_zipcodes = response.json().get("zip_codes")
    return str(zipcode) in philadelphia_zipcodes


def get_close_zipcodes(zipcode, distance, units="miles", minimal=False):
    radius_minimal = "?minimal"
    radius_api_url = f"https://www.zipcodeapi.com/rest/{ZIP_API_KEY}/radius.json/{zipcode}/{distance}/{units}"
    if minimal:
        radius_api_url += radius_minimal

    response = requests.get(radius_api_url)
    return response.json().get('zip_codes')


def get_distances_between_zipcode_and_list(zipcode, other_zipcodes, units="miles"):
    other_zipcodes_text = ",".join([str(x) for x in other_zipcodes])
    url = f"https://www.zipcodeapi.com/rest/{ZIP_API_KEY}/multi-distance.json/{zipcode}/{other_zipcodes_text}/{units}"
    response = requests.get(url)
    return response.json().get('distances')


def get_minimum_distance(distance_dict):
    if distance_dict is None:
        yield None
    for min_value in sorted(distance_dict, key=distance_dict.get):
        yield min_value


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
        testing_sites = TestingSite.objects.all()
        distance_list = get_distances_between_zipcode_and_list(self.zip_code, [site.zipcode for site in testing_sites])
        min_zip = next(get_minimum_distance(distance_list))
        if min_zip is None:
            return None
        return testing_sites.filter(zipcode=min_zip)
