import zipcodes
from django.db import models
from phone_field import PhoneField
from django.utils.translation import gettext_lazy as _
from .utils import GeoNamesClient

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
            f"{self.line_two + ', ' if self.line_two else ''}\n" \
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

    def as_text(self):
        provider_site_text = f"Testing Provider:\n{self.provider_name}\n{self.provider_phone.formatted}"
        if self.provider_alt_phone:
            provider_site_text += f"\n{self.provider_alt_phone.formatted}"
        return provider_site_text

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
        testing_site_text = f"Your closest testing site:\n"\
            f"{self.site_name}\n{self.address}\n{self.site_phone.formatted}\n" \
            f"Call the testing provider to schedule a test:\n{self.provider.as_text()}"
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


def find_closest_address(zipcode, radius=10, max_limit=30, step=10):
    if radius > max_limit:
        raise ValueError("Too far to travel")
    gc = GeoNamesClient()
    zipcodes = {postalcode.get("postalCode"): postalcode.get("distance")
                for postalcode in gc.find_nearby_postal_codes(zipcode, radius=radius)}
    addresses = Address.objects.filter(code__in=zipcodes.keys())
    if len(addresses) == 0:
        # If no addresses, expand search radius
        return find_closest_address(zipcode, radius+step)
    elif len(addresses) == 1:
        # If only one, return one
        return addresses[0]
    else:
        # If more than one, append distance, sort and return min element
        distances = {address: zipcodes[address.code] for address in addresses}
        return sorted(distances, key=distances.get)[0]


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
        # Check for one in the person's zipcode
        closest = Address.objects.filter(code=self.zip_code).first()
        if closest:
            return closest.testingsite_set.first()
        # Find the closest one
        closest_address = find_closest_address(self.zip_code)
        return closest_address.testingsite_set.first()

