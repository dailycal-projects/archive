import os
import re
import boto3
import logging
import datetime
from PIL import Image
from django.core.files import File
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Page, Issue
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Get a list of all files in the archival bucket and, if they aren't already in the database, add them."

    def handle(self, *args, **options):
        # Connect to S3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME)
        # Regex to match raw page PDFs
        page_re = re.compile(r'^.*/dailycal_(\d{4})(\d{2})(\d{2})_(\d{1,2}).pdf')
        # Regex to match issue PDFs
        issue_re = re.compile(r'^.*/dailycal_(\d{4})(\d{2})(\d{2})_issue.pdf')
        # Loop through every file in the bucket
        logger.info('Fetching files from S3...')
        for obj in bucket.objects.page_size(10):
            page_match = re.match(page_re, obj.key)
            issue_match = re.match(issue_re, obj.key)
            if page_match:
                date_parts = [page_match.group(1), page_match.group(2), page_match.group(3)]
                date_parts = [int(d) for d in date_parts]
                date = datetime.date(*date_parts)
                page_number = page_match.group(4)
                page, c = Page.objects.get_or_create(date=date, page_number=page_number)
                # If it's not already in the database
                if c:
                    issue, c = Issue.objects.get_or_create(date=date)
                    page.issue = issue
                    page.save()
                    logger.info('Created {}'.format(page))
                else:
                    logger.debug('Already imported {}'.format(page))
            elif issue_match:
                date_parts = [issue_match.group(1), issue_match.group(2), issue_match.group(3)]
                date_parts = [int(d) for d in date_parts]
                date = datetime.date(*date_parts)
                issue, c = Issue.objects.get_or_create(date=date)
                logger.info('Logged issue PDF for {}'.format(issue))
                issue.pdf_created = True
                issue.save()
