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

    def handle(self, *args, **options):

        # Get a list of all keys in the S3 bucket
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME)
        keys = set([o.key for o in bucket.objects.all()])

        logger.info('{} keys'.format(len(keys)))

        # Walk the tree
        for root, directories, files in os.walk(settings.PROCESSED_DIR):
            for filename in files:
                # Join the two strings in order to form the full filepath
                local_path = os.path.join(root, filename)
                remote_path = os.path.relpath(local_path, settings.PROCESSED_DIR)

                logger.info(remote_path)

                # Check if the key already exists in s3
                if remote_path not in keys:
                    # If not, upload the file
                    logger.info('Uploading')
                    bucket.upload_file(
                        local_path,
                        remote_path,
                        ExtraArgs={'ACL': 'public-read'}
                    )
