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

        for filename in glob.glob(os.path.join(settings.RAW_DIR, '*.pdf')):

            logger.debug('Processing %s' % filename)

            subprocess.call(["pdfimages", "-tiff", filename, filename.split('.')[-2]])
