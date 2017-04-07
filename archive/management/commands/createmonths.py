import os
import csv
import logging
from datetime import date, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Month, Page
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate database with month objects."

    def handle(self, *args, **options):
        for year in range(1900, 2000):
            for month in range(1, 13):
                start_date = date(year, month, 1)
                month_obj, c = Month.objects.get_or_create(date=start_date)
                end_date = start_date + timedelta(weeks=4)
                pages = Page.objects.filter(date__range = (start_date, end_date))