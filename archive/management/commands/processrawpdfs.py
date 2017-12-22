import os
import re
import boto3
import logging
import datetime
import shutil
import glob
from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Page, Issue
import subprocess
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Take scanned TIFs, generate JPEGs and PDFs and upload to \
     the archival bucket."

    def handle(self, *args, **options):

        def get_path(date, page_number):
            return '{0}-{1}-{2}-p{3}'.format(
                date.year,
                date.strftime('%m'),
                date.strftime('%d'),
                format(page_number, '02'))

        for filename in glob.glob(os.path.join(settings.RAW_DIR, '*/*/*.tif')):

            logger.debug('Processing %s' % filename)

            # Extract date and page number from filename
            #this_re = re.compile(r'^.*(\d{4})-(\d{2})[.-](\d{2})(?:[.-]?p|-)(\d{1,2}).pdf')
            this_re = re.compile(r'^.*1965-03-(\d{1,2})-p(\d{1,2}).tif')
            match = re.match(this_re, filename)

            if match:
                date_parts = [
                    1965,
                    3,
                    match.group(1)
                ]
                date_parts = [int(d) for d in date_parts]
                date = datetime.date(*date_parts)
                page_number = int(match.group(2))

                # Move the scan to the processed directory
                raw_path = os.path.join(settings.RAW_DIR, filename)
                renamed_path = os.path.join(settings.RAW_DIR, get_path(date, page_number) + '.tif')
                shutil.copyfile(raw_path, renamed_path)
