from django.conf import settings

def browser(request):
    return {
        'ARCHIVE_BUCKET_URL': 'https://{}/{}/'.format(
        	settings.AWS_S3_HOST,
        	settings.ARCHIVE_BUCKET_NAME),
        'SITE_URL': 'archive.dailycal.org/',
    }