from django.conf.urls import url
from archive.models import Issue
from browser.views import IssueDetailView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView

urlpatterns = [
    url(r'^$',
        ArchiveIndexView.as_view(model=Issue, date_field="date", template_name='browser/issue_archive.html'),
        name="issue_archive"),
    url(r'^(?P<year>[0-9]{4})/$',
        YearArchiveView.as_view(model=Issue, date_field="date", make_object_list = True, template_name='browser/issue_archive_year.html'),
        name="archive_year"),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
        MonthArchiveView.as_view(model=Issue, date_field="date", month_format='%m', template_name='browser/issue_archive_month.html'),
        name="archive_year"),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]+)/$',
        IssueDetailView.as_view(),
        name="issue_detail"
    )
]