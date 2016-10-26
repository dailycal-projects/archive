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
        # For every issue that doesn't have a PDF
        # (This relies on running updatedatabase first)
        for issue in Issue.objects.filter(pdf_created=False):
            logger.info(issue)
            issue.save_pdf()
            issue.upload_file(issue.local_path(issue.pdf_path))
            issue.pdf_created = True
            issue.save()