import os
import csv
import logging
from datetime import date
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Month
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'sponsors.csv')
        with open(path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                d = date(int(row['year']), int(row['month']), 1)
                Month.objects.filter(date=d).update(sponsor=row['name'])
