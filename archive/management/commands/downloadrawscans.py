import os
import boto3
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Downloads all files in the raw files S3 bucket."

    def handle(self, *args, **options):
        # Connect to S3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.RAW_BUCKET_NAME)

        # Loop through all files in the bucket
        for obj in bucket.objects.page_size(10):
            # Flatten directory structure
            local_path = os.path.join(
                settings.RAW_DIR,
                obj.key.replace('/', '-')
            )
            # If we don't already have it
            if not os.path.exists(local_path):
                logger.debug('Downloading {}'.format(obj.key))
                # Download it
                bucket.download_file(obj.key, local_path)
                # And delete it from the bucket
                obj.delete()
