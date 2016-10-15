import os
import boto3
import pytesseract
from PIL import Image
from PyPDF2 import PdfFileMerger
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.core.files import File
from tempfile import TemporaryFile

class ArchivedFileModel(models.Model):

    def local_path(self, filename):
        return os.path.join(
            settings.PROCESSED_DIR, filename)

    def upload(self, path):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.ARCHIVE_BUCKET_NAME)
        local_path = self.local_path(path)
        bucket.upload_file(
            local_path,
            path,
            ExtraArgs={"ACL": "public-read"}
        )

    class Meta:
        abstract = True


class Page(ArchivedFileModel):
    """A single page from an issue."""

    date = models.DateField()
    page_number = models.IntegerField()
    text = models.TextField()
    issue = models.ForeignKey('Issue', null=True, related_name='pages')

    @property
    def path(self):
        return '{0}/{1}/{2}/dailycal_{0}{1}{2}_{3}'.format(
            self.date.year,
            self.date.strftime('%m'),
            self.date.strftime('%d'),
            format(self.page_number,'02'))

    @property
    def tif(self):
        return self.path + '.tif'

    @property
    def local_tif_path(self):
        return self.local_path(self.tif)

    def has_tif(self):
        return os.path.exists(self.local_tif_path)

    def upload_tif(self):
        if self.has_tif:
            self.upload(self.tif)
        else:
            raise Exception('No local TIF file!')

    @property
    def jpg(self):
        return self.path + '.jpg'

    @property
    def local_jpg_path(self):
        return self.local_path(self.jpg)

    def has_jpg(self):
        return os.path.exists(self.local_jpg_path)

    def save_jpg(self):
        if self.has_tif:
            tif_file = Image.open(self.local_tif_path)
            with open(self.local_jpg_path, 'wb') as f:
                tif_file.save(f, 'JPEG')
        else:
            raise Exception('No tif file to generate JPG from!')

    def upload_jpg(self):
        if self.has_jpg:
            self.upload(self.jpg)
        else:
            raise Exception('No local JPG file!')
    
    @property
    def pdf(self):
        return self.path + '.pdf'

    @property
    def local_pdf_path(self):
        return self.local_path(self.pdf)

    def has_pdf(self):
        return os.path.exists(self.local_pdf_path)

    def save_pdf(self):
        if self.has_tif:
            tif_file = Image.open(self.local_tif_path)
            with open(self.local_pdf_path, 'wb') as f:
                tif_file.save(f, 'PDF')
        else:
            raise Exception('No tif file to generate PDF from!')

    def upload_pdf(self):
        if self.has_pdf:
            self.upload(self.pdf)
        else:
            raise Exception('No local PDF file!')

    def __str__(self):
        return '{}: p. {}'.format(self.date, self.page_number)

    class Meta:
        ordering = ['-date','page_number']
        unique_together = (('date', 'page_number'),)


class Issue(ArchivedFileModel):
    date = models.DateField(unique=True)
    sponsor = models.CharField(
        max_length=200,
        null=True,
        blank=False
    )
    pdf_created = models.BooleanField(default=False)

    @property
    def date_parts_list(self):
        """List of year, month, day."""
        return [self.date.strftime('%Y'), self.date.strftime('%m'), self.date.strftime('%d')]

    @property
    def date_parts_dict(self):
        return {
            'year': self.date.strftime('%Y'),
            'month': self.date.strftime('%m'),
            'day': self.date.strftime('%d')
        }
    
    @property
    def directory(self):
        return '{0}/{1}/{2}'.format(*self.date_parts_list)

    @property
    def path(self):
        return '{0}/{1}/{2}/dailycal_{0}{1}{2}_issue'.format(*self.date_parts_list)

    @property
    def pdf(self):
        return self.path + '.pdf'

    @property
    def local_pdf_path(self):
        return self.local_path(self.pdf)

    def has_pdf(self):
        return os.path.exists(self.local_pdf_path)

    def save_pdf(self):
        outfile = PdfFileMerger()
        for page in self.pages.all():
            # If we don't already have the PDF
            if not page.has_pdf:
                # Try to create it
                if page.has_tif:
                    page.save_pdf()
                # Or download it
                else:
                    bucket.download_file(page.pdf, page.local_pdf_path)
            outfile.append(page.local_pdf_path)

        # Write the issue PDF
        issue_path = os.path.join(settings.PROCESSED_DIR, self.pdf)
        issue_pdf = open(issue_path, 'w+')
        outfile.write(issue_path)

    def upload_pdf(self):
        if self.has_pdf:
            self.upload(self.pdf)
        else:
            raise Exception('No local PDF file!')

    def process(self):
        for page in self.pages.all():
            if page.has_tif:
                page.upload_tif()
                page.save_jpg()
                page.upload_jpg()
                page.save_pdf()
                page.upload_pdf()
        self.save_pdf()
        self.upload_pdf()

    def __str__(self):
        return '{}'.format(self.date)

    class Meta:
        ordering = ['-date']
