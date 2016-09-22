import os
import datetime
import pytesseract
from PIL import Image
from django.core.files import File
from django.conf import settings
from django.core.management.base import BaseCommand
from archive.models import Page, Issue


class Command(BaseCommand):
    help = ""

    def create_issue_PDFs(self):
        for issue in Issue.objects.filter(pdf=None):
            issue.create_pdf()

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            dest='flush',
            default=False,
            help='Delete all pages in the database and start anew.',
        )
        parser.add_argument(
            '--ocr',
            action='store_true',
            dest='ocr',
            default=False,
            help='OCR scanned images.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            Page.objects.all().delete()
        dir_path = os.path.join(
            settings.BASE_DIR, 'scans')
        for filename in os.listdir(dir_path):
            if filename.endswith('.tif'):
                print(filename)
                try:
                    # Extract date and page number from filename
                    year, month, day, page = filename.split('-')
                    date = datetime.date(int(year), int(month), int(day))
                    page_number = int(page.split('.')[0][1:])
                    # Check if this page has already been imported
                    page, created = Page.objects.get_or_create(
                        date = date,
                        page_number = page_number,
                    )
                    if created:
                        # Create an Issue if one doesn't exist
                        issue, created = Issue.objects.get_or_create(
                            date = date
                        )
                        page.issue = issue
                        # Save the scan
                        filepath = os.path.join(dir_path, filename)
                        scanned_file = File(open(filepath,'rb'))
                        page.scanned_img.save('', scanned_file)
                        # Create pdf
                        page.create_pdf(scanned_file)
                        page.save()
                    else:
                        print('Already imported {}'.format(filename))
                except ValueError:
                    print('Error: check filename format for {}'.format(filename))

        self.create_issue_PDFs()
