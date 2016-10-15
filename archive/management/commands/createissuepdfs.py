import os
import boto3
import logging
from PyPDF2 import PdfFileMerger
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Issue
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Concatenate page PDFs to create issue PDFs."

    def handle(self, *args, **options):
        # Connect to S3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME)

        # For every issue that doesn't have a PDF
        # (This relies on running updatedatabase first)
        for issue in Issue.objects.filter(pdf_created=False):
            logger.info('Creating issue PDF for {}'.format(issue))

            # Make sure the issue directory exists locally
            local_path = os.path.join(
                settings.PROCESSED_DIR, issue.directory)
            if not os.path.exists(local_path):
                os.makedirs(local_path)
            
            outfile = PdfFileMerger()

            # For all the pages in this issue
            for page in issue.pages.all():
                # If we don't already have the PDF
                if not page.has_pdf:
                    logger.info(
                        'Downloading page {}'.format(page.page_number))
                    #page_pdf = open(page.local_pdf_path, 'w+')
                # Try to create it
                elif page.has_tif:
                    page.save_pdf()
                # Or download it
                else:
                    bucket.download_file(page.pdf, page.local_pdf_path)
                outfile.append(page.local_pdf_path)

            # Write the issue PDF
            issue_path = os.path.join(settings.PROCESSED_DIR, issue.pdf)
            issue_pdf = open(issue_path, 'w+')
            outfile.write(issue_path)

            # Upload the issue PDF to the archival bucket
            logger.info('Uploading issue PDF')
            bucket.upload_file(issue_path, issue.pdf)

            issue.pdf_created = True
            issue.save()
