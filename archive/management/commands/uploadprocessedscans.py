import os
import boto3
import botocore
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Uploads the files in the local processed folder to the Archive S3 bucket."

    def handle(self, *args, **options):
        # Connect to S3
        session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
        )
        s3 = session.resource('s3')
        bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME) 

        local_processed_path = settings.PROCESSED_DIR
        for (dirpath, _, filenames) in os.walk(local_processed_path):
            for name in filenames:
                path = os.path.join(dirpath, name)
                key = path[len(local_processed_path)+1:]

                # Checking if the file exists already in the S3 bucket
                try:
                    s3.Object(settings.ARCHIVE_BUCKET_NAME, key).load()
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        with open(path, 'rb') as data:
                            logger.debug('Uploading {}'.format(key))
                            bucket.put_object(Key=key, Body=data)
                    else:
                        logger.debug('ERROR')
                else:
                    logger.debug('{} does exist in bucket'.format(key))