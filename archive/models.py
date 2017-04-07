import os
import re
import boto3
import deepzoom
import pytesseract
from subprocess import call
from PIL import Image
from lxml import html
from django.db import models
from datetime import datetime, date, timedelta
from django.utils import timezone
from PyPDF2 import PdfFileMerger
from django.conf import settings
from django.urls import reverse
from django.core.files import File
from tempfile import TemporaryFile


class ArchivedFileModel(models.Model):
    """
    Base model for pages and issues.
    """

    def local_path(self, path):
        return os.path.join(
            settings.PROCESSED_DIR,
            path
        )

    def upload_file(self, path):
        """
        Upload to the archival bucket.
        """
        local_path = self.local_path(path)
        if os.path.exists(local_path):
            s3 = boto3.resource('s3')
            bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME)
            bucket.upload_file(
                local_path,
                path,
                ExtraArgs={'ACL': 'public-read'}
            )
        else:
            raise Exception('Local file not found.')

    class Meta:
        abstract = True


class Page(ArchivedFileModel):
    """
    A single page from an issue.
    """
    date = models.DateField()
    page_number = models.IntegerField()
    text = models.TextField()
    issue = models.ForeignKey('Issue', null=True, related_name='pages')
    processed_datetime = models.DateTimeField(null=True)

    @property
    def filename(self):
        return '{0}/{1}/{2}/dailycal_{0}{1}{2}_{3}'.format(
            self.date.year,
            self.date.strftime('%m'),
            self.date.strftime('%d'),
            format(self.page_number,'02'))

    @property
    def tif_path(self):
        return self.filename + '.tif'

    @property
    def jpg_path(self):
        return self.filename + '.jpg'

    def save_jpg(self):
        """
        Save a JPG version of this page.
        """
        # Check that the tif exists locally
        local_tif_path = self.local_path(self.tif_path)
        if os.path.exists(local_tif_path):
            tif_file = Image.open(local_tif_path)
            # Save a JPG version
            local_jpg_path = self.local_path(self.jpg_path)
            with open(local_jpg_path, 'wb') as f:
                tif_file.save(f, 'JPEG')
        else:
            raise Exception('No TIF to generate JPG from.')

    @property
    def pdf_path(self):
        return self.filename + '.pdf'

    def save_pdf(self):
        """
        Save a PDF version of this page.
        """
        # Check that the tif exists locally
        local_tif_path = self.local_path(self.tif_path)
        if os.path.exists(local_tif_path):
            tif_file = Image.open(local_tif_path)
            # Save a PDF version
            local_pdf_path = self.local_path(self.pdf_path)
            with open(local_pdf_path, 'wb') as f:
                tif_file.save(f, 'PDF')
        else:
            raise Exception('No TIF file to generate PDF from.')

    def process(self):
        """
        Generate JPG and PDF versions from the raw image. Run the raw image
        through tesseract to generate an hOCR file, and import the text
        from that file into the database.
        """
        self.save_jpg()
        self.save_pdf()
        #self.save_hocr_file()
        #self.save_ocr_text()
        self.processed_datetime = timezone.now()
        self.save()

    def upload(self):
        """
        Upload TIF, JPG, hOCR and PDF.
        """
        self.upload_file(self.tif_path)
        self.upload_file(self.jpg_path)
        #self.upload_file(self.local_path(self.hocr_path))
        self.upload_file(self.pdf_path)

    @property
    def hocr_path(self):
        return self.filename + '.hocr'

    def save_hocr_file(self):
        """
        Generate hOCR file using tesseract.
        """
        tif_path = self.local_path(self.tif_path)
        call([
            'tesseract',
            tif_path,
            self.local_path(self.filename),
            '-c language_model_penalty_non_freq_dict_word=4',
            '-c language_model_penalty_non_dict_word=2',
            'hocr',
        ])

    def save_ocr_text(self):
        """
        Save raw hOCR text to database. Adapted from
        https://github.com/tmbdev/hocr-tools/blob/master/hocr-lines
        """
        hocr_path = self.local_path(self.filename + '.hocr')
        
        if not os.path.exists(hocr_path):
            raise Exception('This page does not have an hOCR file.')

        text = ''

        doc = html.parse(hocr_path)
        lines = doc.xpath("//*[@class='ocr_line']")

        for line in lines:
            textnodes = line.xpath(".//text()")
            s = ''.join([text for text in textnodes])
            text += re.sub(r'\s+',' ',s)

        self.text = text
        self.save()

    def __str__(self):
        return '{}: p. {}'.format(self.date, self.page_number)

    class Meta:
        ordering = ['date','page_number']
        unique_together = (('date', 'page_number'),)


class Issue(ArchivedFileModel):
    """
    A single issue published on a particular day.
    """
    date = models.DateField(unique=True)
    pdf_created = models.BooleanField(default=False)

    @property
    def date_parts_list(self):
        """
        List of [year, month, day].
        """
        return [
            self.date.strftime('%Y'),
            self.date.strftime('%m'),
            self.date.strftime('%d')
        ]

    @property
    def date_parts_dict(self):
        """
        Dict of {"year": year, "month": month, "day": day}.
        """
        return {
            'year': self.date.strftime('%Y'),
            'month': self.date.strftime('%m'),
            'day': self.date.strftime('%d')
        }
    
    @property
    def directory(self):
        return '{0}/{1}/{2}'.format(*self.date_parts_list)

    @property
    def filename(self):
        return '{0}/{1}/{2}/dailycal_{0}{1}{2}_issue'.format(
            *self.date_parts_list
        )

    @property
    def pdf_path(self):
        return self.filename + '.pdf'

    def save_pdf(self):
        """
        Generate the issue PDF. Assumes all page PDFs exist locally.
        """
        outfile = PdfFileMerger()

        # Add PDF for each page in the issue
        for page in self.pages.all():
            local_pdf_path = page.local_path(page.pdf_path)
            outfile.append(local_pdf_path)

        # Write the issue PDF
        local_pdf_path = self.local_path(self.pdf_path)
        issue_pdf = open(local_pdf_path, 'w+')
        issue_pdf.close()
        outfile.write(local_pdf_path)

    def upload_pdf(self):
        """
        Upload issue PDF.
        """
        self.upload_file(self.local_path(self.pdf_path))

    def process(self):
        """
        Process pages and generate PDF.
        """
        for page in self.pages.all():
            page.process()

        self.save_pdf()

    def upload(self):
        """
        Upload pages and issue PDF.
        """
        for page in self.pages.all():
            page.upload()

        self.upload_pdf()

    def upload_directory(self):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME)

        # Walk the tree.
        for root, directories, files in os.walk(self.local_path(self.directory)):
            for filename in files:
                # Join the two strings in order to form the full filepath.
                local_path = os.path.join(root, filename)
                remote_path = os.path.join(
                    self.directory,
                    os.path.relpath(local_path, self.local_path(self.directory))
                )

                bucket.upload_file(
                    local_path,
                    remote_path,
                    ExtraArgs={'ACL': 'public-read'}
                )

    def __str__(self):
        return '{}'.format(self.date)

    class Meta:
        ordering = ['date']


class Month(models.Model):
    sponsor = models.CharField(
        max_length=200,
        null=True,
        blank=False
    )
    date = models.DateField(unique=True)

    def get_pages(self):
        start_date = self.date
        end_date = start_date + timedelta(weeks=4)
        pages = Page.objects.filter(date__range = (start_date, end_date))
        return pages

    @property
    def available(self):
        pages = self.get_pages()
        if pages:
            return True
        else:
            return False

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.date.strftime('%b %Y')
