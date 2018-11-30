import os
import boto3
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Downloads all files in the raw files S3 bucket (download local copy of existing files)."

    def handle(self, *args, **options):
        # Connect to S3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME) 
        # Loop through all files in the bucket
        for obj in bucket.objects.page_size(10):
            # Flatten directory structure
            local_path = os.path.join(
                settings.RAW_DIR,
                obj.key.replace('/', '-')
            )
            # If we don't already have it then...
            if not os.path.exists(local_path):
                fname = obj.key.replace('/', '-')
                if (len(fname.split('-')) == 4):
                    year, month, day, scan = fname.split('-')
                    if not os.path.exists(settings.PROCESSED_DIR + "/" + year + "/" + month + "/" + day + "/"  + scan):            
                        logger.debug('Downloading {}'.format(obj.key))
                        # ...Download it
                        bucket.download_file(obj.key, local_path)

                        # And delete it from the bucket (no thanks.)
                        # obj.delete()
