import os
import re
import boto3
import logging
import datetime
import shutil
from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Page, Issue
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Take page PDFs, generate JPEGs and upload to \
     the archival bucket."

    def get_path(date, page_number):
        return '{0}/{1}/{2}/dailycal_{0}{1}{2}_{3}'.format(
            date.year,
            date.strftime('%m'),
            date.strftime('%d'),
            format(page_number, '02'))

    def handle(self, *args, **options):
        # Connect to S3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME)

        for filename in os.listdir(settings.RAW_DIR):
            if filename.endswith('.pdf'):
                logger.debug('Processing {}'.format(filename))

                # Extract date and page number from filename
                re_2012 = re.compile(r'^(\d{4})-(\d{2}).(\d{2}).(\d{4}).*dailycal(\d{2}).pdf')
                match = re.match(tif_re, filename)

                if match:
                    date_parts = [
                        match.group(1), match.group(2), match.group(3)]
                    date_parts = [int(d) for d in date_parts]
                    date = datetime.date(*date_parts)
                    page_number = int(match.group(5))

                    # Check if this page is already in the database
                    page, c = Page.objects.get_or_create(
                        date=date,
                        page_number=page_number,
                    )

                    # If not
                    if c:
                        # Create an Issue if one doesn't exist
                        issue, c = Issue.objects.get_or_create(
                            date=date
                        )
                        page.issue = issue
                        page.save()

                        # Check if the issue folder exists. If not, create it.
                        path = os.path.join(
                            settings.PROCESSED_DIR, issue.directory)
                        if not os.path.exists(path):
                            os.makedirs(path)

                        # Move the pdf to the processed directory
                        raw_path = os.path.join(settings.RAW_DIR, filename)
                        pdf_path = os.path.join(
                            settings.PROCESSED_DIR, page.pdf)
                        shutil.copyfile(raw_path, tif_path)

                        # Upload the pdf
                        bucket.upload_file(pdf_path, page.pdf)

                        scan = Image.open(pdf_path)

                        # Create a jpg
                        jpg_path = os.path.join(
                            settings.PROCESSED_DIR, page.jpg)
                        with open(jpg_path, 'wb') as f:
                            scan.save(f, 'JPEG')
                        # Upload it
                        bucket.upload_file(jpg_path, page.jpg)

                        # Delete the pdf from the raw directory
                        os.remove(raw_path)

                        logger.info('Uploaded {}'.format(page))

                    # If the page is already in the database
                    else:
                        logger.debug('Already uploaded')
                # No match
                else:
                    logger.error('Invalid filename format')
