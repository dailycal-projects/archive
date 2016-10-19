import os
import boto3
import logging
from datetime import date
from PyPDF2 import PdfFileMerger
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Issue
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reprocess all files in the database."

    def handle(self, *args, **options):
        d = date(1964,4,24)
        for issue in Issue.objects.filter(date__lte=d):
            logger.info('Processing {}'.format(issue))
            issue.process()