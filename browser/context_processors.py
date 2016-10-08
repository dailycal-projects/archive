def browser(request):
    return {
        'ARCHIVE_BUCKET_URL': 'https://s3-us-west-1.amazonaws.com/dailycal-archive/',
        'SITE_URL': 'archive.dailycal.org/',
    }