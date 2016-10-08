from archive.models import Issue
from django.conf.urls import url
from browser.views import HomeView, SponsorView, AboutView, IssueDetailView, MonthListView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView

urlpatterns = [
    # Static pages
    url(r'^$',
        HomeView.as_view(),
        name="home"),
    url(r'^sponsor/$',
        SponsorView.as_view(),
        name="sponsor"),
    url(r'^about/$',
        AboutView.as_view(),
        name="about"),
    # Issue pages
    url(r'^issues/$',
        MonthListView.as_view(),
        name="issue_archive"),
    url(r'^issues/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
        MonthArchiveView.as_view(model=Issue, date_field="date", month_format='%m', template_name='browser/issue_archive_month.html'),
        name="archive_month"),
    url(r'^issues/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]+)/$',
        IssueDetailView.as_view(),
        name="issue_detail"
    )
]