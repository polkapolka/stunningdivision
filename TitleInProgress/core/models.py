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
    # TODO: implement
    return True


# TODO: Implement
class FakeTestingSite(object):
    def __init__(self, testing_site_type, zip_code):
        self.testing_site_type = testing_site_type
        self.zip_code = zip_code

    def as_text(self):
        return f"{self.testing_site_type}:\n123 Testing Drive\nVillageville, State {self.zip_code}"


class UserQuestionnaire(models.Model):
    class TestingSiteTypes(models.TextChoices):
        WALK_UP = 'WU', _('Walk up')
        DRIVE_THROUGH = 'DT', _('Drive Through')

    user_id = models.CharField(_("User identifier"), max_length=1024, primary_key=True)

    wants_questionnaire = models.BooleanField(default=None, null=True)
    is_experiencing_symptoms = models.BooleanField(default=None, null=True)
    is_high_risk = models.BooleanField(default=None, null=True)
    has_severe_worsening_symptoms = models.BooleanField(default=None, null=True)

    preferred_testing_site_type = models.CharField(
        max_length=2,
        choices=TestingSiteTypes.choices,
        default=None,
        null=True
    )

    zip_code = models.CharField(max_length=6, default=None, null=True)

    def process_response(self, current_text):
        if self.wants_questionnaire is None:
            if current_text == 'Y':
                self.wants_questionnaire = True
            elif current_text == 'N':
                self.wants_questionnaire = False
            return

        if self.is_experiencing_symptoms is None:
            if current_text == 'Y':
                self.is_experiencing_symptoms = True
            elif current_text == 'N':
                self.is_experiencing_symptoms = False
            return

        if self.is_high_risk is None:
            if current_text == 'Y':
                self.is_high_risk = True
            elif current_text == 'N':
                self.is_high_risk = False
            return

        if self.has_severe_worsening_symptoms is None:
            if current_text == 'Mild':
                self.has_severe_worsening_symptoms = False
            elif current_text in {'Worsening', 'Severe'}:
                self.has_severe_worsening_symptoms = True
            return

        if self.preferred_testing_site_type is None:
            if current_text == 'Walk up':
                self.preferred_testing_site_type = UserQuestionnaire.TestingSiteTypes.WALK_UP
            elif current_text == 'Drive through':
                self.preferred_testing_site_type = UserQuestionnaire.TestingSiteTypes.DRIVE_THROUGH
            return

        if self.zip_code is None:
            if is_valid_zip_code(current_text):
                self.zip_code = current_text
            return

    def get_closest_testing_site(self):
        if self.zip_code is None:
            raise ValueError("zip code is not set. Cannot find closest testing site")
        return FakeTestingSite(self.preferred_testing_site_type, self.zip_code)


