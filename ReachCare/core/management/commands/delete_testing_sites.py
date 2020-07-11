# lake/management/commands/setup_groups.py
import sys
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import Address, TestingSite, Provider

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = "Deletes all records in TestingSite, Address, and Provider Tables"
    def handle(self, *args, **options):
        logger.info("Deleting All TestingSite Records...")
        logger.info(f"Number of Testing Sites: {TestingSite.objects.count()}")
        user_input = input("Are you sure you want to delete all the TestingSite records? (Y/N)")
        if user_input.strip() == 'Y':
            TestingSite.objects.all().delete()
            logger.info(f"Number of Testing Sites: {TestingSite.objects.count()}")
            logger.info(f"Testing sites deleted.")

            logger.info("Deleting All Address Records...")
        else:
            return
        user_input = ''
        logger.info("Deleting All Address Records...")
        logger.info(f"Number of Addresses: {Address.objects.count()}")
        user_input = input("Are you sure you want to delete all the Address records? (Y/N)")
        if user_input.strip() == 'Y':

            Address.objects.all().delete()
            logger.info(f"Number of Addresses: {Address.objects.count()}")
            logger.info(f"Addresses deleted.")
        else:
            return
        user_input = ''
        logger.info("Deleting All Provider Records...")
        user_input = input("Are you sure you want to delete all the Provider records? (Y/N)")
        if user_input.strip() == 'Y':
            logger.info("Deleting All Provider Records...")
            logger.info(f"Number of Providers: {Provider.objects.count()}")
            Provider.objects.all().delete()
            logger.info(f"Number of Providers: {Provider.objects.count()}")
            logger.info(f"Providers deleted.")
        else:
            return

