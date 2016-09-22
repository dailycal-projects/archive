import pytesseract
from PIL import Image
from PyPDF2 import PdfFileMerger
from django.db import models
from django.core.files import File
from tempfile import TemporaryFile

def scan_path(instance, filepath):
    return '{}.tif'.format(
        instance.canonical_path)

def pdf_path(instance, filepath):
    return '{}.pdf'.format(
        instance.canonical_path)

class Page(models.Model):
    date = models.DateField()
    page_number = models.IntegerField()
    scanned_img = models.ImageField(null=True, upload_to=scan_path)
    pdf = models.FileField(null=True, upload_to=pdf_path)
    text = models.TextField()
    issue = models.ForeignKey('Issue', null=True, related_name='pages')

    @property
    def canonical_path(self):
        return '{0}/{1}/{2}/dailycal_{0}{1}{2}_{3}'.format(
            self.date.year,
            self.date.strftime('%m'),
            self.date.strftime('%d'),
            format(self.page_number,'02'))

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


class Issue(models.Model):
    date = models.DateField()
    pdf = models.FileField(null=True, upload_to=pdf_path)

    def create_pdf(self):
        """
        Concatenate PDFs from individual pages.
        """
        outfile = PdfFileMerger()
        for page in self.pages.all():
            if not page.pdf:
                page.create_pdf()
            outfile.append(page.pdf.file)

        with TemporaryFile() as f:
            outfile.write(f)
            self.pdf.save('', File(f))

    @property
    def canonical_path(self):
        return '{0}/{1}/{2}/dailycal_{0}{1}{2}'.format(
            self.date.year,
            self.date.strftime('%m'),
            self.date.strftime('%d'))

    def __str__(self):
        return '{}'.format(self.date)
