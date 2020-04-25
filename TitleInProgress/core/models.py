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
