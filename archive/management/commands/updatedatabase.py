import os
import re
import boto3
import datetime
import pytesseract
from PIL import Image
from django.core.files import File
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Page, Issue
from tempfile import TemporaryFile


class Command(BaseCommand):
    help = "Get a list of all files in the archival bucket and, if they aren't already in the database, add them."

    def handle(self, *args, **options):
        # Connect to S3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('dailycal-archive')
        # Regex to match raw .tif scans
        p = re.compile(r'^.*/dailycal_(\d{4})(\d{2})(\d{2})_(\d{1,2}).tif')
        # Loop through every file in the bucket
        print('Fetching files from S3...')
        for obj in bucket.objects.page_size(10):
            match = re.match(p, obj.key)
            if match:
                date_parts = [match.group(1), match.group(2), match.group(3)]
                date_parts = [int(d) for d in date_parts]
                date = datetime.date(*date_parts)
                page_number = match.group(4)
                page, c = Page.objects.get_or_create(date=date, page_number=page_number)
                # If it's not already in the database
                if c:
                    issue, c = Issue.objects.get_or_create(date=date)
                    page.issue = issue
                    page.save()
                    print('Created {}'.format(page))
                else:
                    print('Already imported {}'.format(page))
