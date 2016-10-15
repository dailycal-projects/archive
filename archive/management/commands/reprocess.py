import os
import boto3
import logging
from PyPDF2 import PdfFileMerger
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Issue
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reprocess all files in the database."

    def handle(self, *args, **options):
        for issue in Issue.objects.all():
            logger.info('Processing {}'.format(issue))
            issue.process()