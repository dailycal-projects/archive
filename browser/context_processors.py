from django.conf import settings

def browser(request):
    return {
        'ARCHIVE_BUCKET_URL': 'https://{}.{}/'.format(
        	settings.ARCHIVE_BUCKET_NAME,
        	settings.AWS_S3_HOST,
        	),
        'SITE_URL': 'archive.dailycal.org/',
    }