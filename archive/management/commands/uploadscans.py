import os
import boto3
import logging
import datetime
from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Page, Issue
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Take scanned .tif files, generate .jpgs and .pdfs and upload to \
     the archival bucket."

    def get_path(date, page_number):
        return '{0}/{1}/{2}/dailycal_{0}{1}{2}_{3}'.format(
            date.year,
            date.strftime('%m'),
            date.strftime('%d'),
            format(page_number,'02'))

    def handle(self, *args, **options):
        # Connect to S3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME)
        dir_path = os.path.join(
            settings.BASE_DIR, 'scans')
        for filename in os.listdir(dir_path):
            if filename.endswith('.tif'):
                logger.debug(filename)
                try:
                    # Extract date and page number from filename
                    year, month, day, page = filename.split('-')
                    date = datetime.date(int(year), int(month), int(day))
                    page_number = int(page.split('.')[0][1:])
                    # Check if this page has already been imported
                    page, c = Page.objects.get_or_create(
                        date = date,
                        page_number = page_number,
                    )
                    if c:
                        # Create an Issue if one doesn't exist
                        issue, c = Issue.objects.get_or_create(
                            date = date
                        )
                        page.issue = issue
                        page.save()

                        # Check if the issue folder exists. If not, create it.
                        path = os.path.join(settings.PROCESSED_FILES_DIR, issue.directory)
                        if not os.path.exists(path):
                            os.makedirs(path)

                        # Upload the scan
                        filepath = os.path.join(dir_path, filename)
                        bucket.upload_file(filepath, page.path + '.tif')
                        filepath = os.path.join(dir_path, filename)
                        scan = Image.open(filepath)

                        # We get odd behavior with Python's tempfile module,
                        # so we're just going to create our own

                        # Create a jpg
                        jpg_path = os.path.join(settings.PROCESSED_FILES_DIR, page.jpg)
                        with open(jpg_path, 'wb') as f:
                            scan.save(f, 'JPEG')
                        bucket.upload_file(jpg_path, page.jpg)
                        # Create a pdf
                        pdf_path = os.path.join(settings.PROCESSED_FILES_DIR, page.pdf)
                        with open(pdf_path, 'wb') as f:
                            scan.save(f, 'PDF')
                        bucket.upload_file(pdf_path, page.pdf)
                        logger.info('   Uploaded')
                    else:
                        logger.debug('   Already uploaded')
                except ValueError:
                    logger.error('   Invalid filename format')
