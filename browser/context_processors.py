from django.conf import settings

def browser(request):
    return {
        'ARCHIVE_BUCKET_URL': 'https://{}/{}/'.format(
        	's3-us-west-2.amazonaws.com',
        	settings.ARCHIVE_BUCKET_NAME,
        	),
        'SITE_URL': 'archive.dailycal.org/',
    }