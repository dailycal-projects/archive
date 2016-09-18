from django.db import models

def scan_path(instance, filename):
    return '{0}/{1}/{2}/p{3}.tif'.format(instance.date.year, instance.date.month, instance.date.day, instance.page)

class Page(models.Model):
    date = models.DateField()
    page = models.IntegerField()
    scan = models.ImageField(null=True, upload_to=scan_path)
    text = models.TextField()

    def __str__(self):
        return '{}: Page {}'.format(self.date, self.page)