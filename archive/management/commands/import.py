import os
import datetime
import pytesseract
from PIL import Image
from django.core.files import File
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Page


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        Page.objects.all().delete()
        dir_path = os.path.join(
            settings.BASE_DIR, 'scans')
        for filename in os.listdir(dir_path):
            if filename.endswith('.tif'):
                print(filename)
                filepath = '{}/{}'.format(dir_path, filename)
                year, month, day, page = filename.split('-')
                page = int(page.split('.')[0][1:])
                scanned_image = Image.open(filepath)
                text = pytesseract.image_to_string(scanned_image, lang='ENG')
                page = Page(
                    date = datetime.date(int(year), int(month), int(day)),
                    page = page,
                    text = text
                )
                scanned_file = File(open(filepath,'rb'))
                page.scan.save('', scanned_file)
                page.save()
                