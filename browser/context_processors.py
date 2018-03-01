from django.conf import settings

def browser(request):
    return {
        'ARCHIVE_BUCKET_URL': 'https://{}.{}/'.format(
        	settings.ARCHIVE_BUCKET_NAME,
        	's3-us-west-2.amazonaws.com',
        	),
        'SITE_URL': 'archive.dailycal.org/',
    }