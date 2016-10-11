import pytesseract
from django.urls import reverse
from PIL import Image
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
    def jpg(self):
        return self.path + '.jpg'
    
    @property
    def pdf(self):
        return self.path + '.pdf'

    def ocr(self):
        scan = Image.open(self.scanned_img)
        self.text = pytesseract.image_to_string(scan, lang='ENG')
        self.save()

    def __str__(self):
        return '{}: p. {}'.format(self.date, self.page_number)

    class Meta:
        ordering = ['-date','page_number']
        unique_together = (('date', 'page_number'),)


class Issue(models.Model):
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

    def __str__(self):
        return '{}'.format(self.date)
