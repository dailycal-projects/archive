import pytesseract
from PIL import Image
from PyPDF2 import PdfFileMerger
from django.db import models
from django.core.files import File
from tempfile import TemporaryFile


class Page(models.Model):
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
    def image(self):
        return self.path + '.jpg'
    
    @property
    def pdf(self):
        return self.path + '.pdf'

    def ocr(self):
        scan = Image.open(self.scanned_img)
        self.text = pytesseract.image_to_string(scan, lang='ENG')
        self.save()

    def create_pdf(self, image):
        with TemporaryFile() as f:
            scan = Image.open(image)
            scan.save(f, "PDF")
            self.pdf.save('', File(f))

    def __str__(self):
        return '{}: p. {}'.format(self.date, self.page_number)

    class Meta:
        ordering = ['-date','page_number']
        unique_together = (('date', 'page_number'),)


class Issue(models.Model):
    date = models.DateField(unique=True)
    #pdf = models.FileField(null=True, upload_to=pdf_path)
    sponsor = models.CharField(
        max_length=200,
        null=True,
        blank=False
    )

    """
    def create_pdf(self):

        outfile = PdfFileMerger()
        for page in self.pages.all():
            if not page.pdf:
                page.create_pdf()
            outfile.append(page.pdf.file)

        with TemporaryFile() as f:
            outfile.write(f)
            self.pdf.save('', File(f))"""

    @property
    def canonical_path(self):
        return '{0}/{1}/{2}/dailycal_{0}{1}{2}'.format(
            self.date.year,
            self.date.strftime('%m'),
            self.date.strftime('%d'))

    def __str__(self):
        return '{}'.format(self.date)
