import random
import calendar
from django.urls import reverse
from datetime import datetime
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from bakery.views import BuildableDetailView, BuildableListView, BuildableTemplateView, BuildableMonthArchiveView
from archive.models import Issue, Page, Month

class HomeView(BuildableTemplateView):
    template_name = 'browser/home.html'
    build_path = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['issue_count'] = Issue.objects.count()
        context['page_count'] = Page.objects.count()
        # Get a list of issues to randomize from
        context['random_issue_urls'] = [] 
        for i in range(0, 10):
            random_index = random.randint(0, context['issue_count'] - 1)
            random_issue = Page.objects.all()[random_index]
            context['random_issue_urls'].append(
                reverse(
                    'issue_detail',
                    args=[random_issue.date.year,
                         format(
                            random_issue.date,
                            '%m'),
                         format(
                            random_issue.date,
                            '%d')
                         ]
                    )
            )
        return context


class SponsorView(BuildableTemplateView):
    template_name = 'browser/sponsor.html'
    build_path = 'sponsor/index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SponsorView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the months that have been sponsored
        context['sponsored_months'] = Month.objects.exclude(sponsor=None)

        return context


class AboutView(BuildableTemplateView):
    template_name = 'browser/about.html'
    build_path = 'about/index.html'


class MonthListView(BuildableListView):
    template_name = 'browser/issue_archive.html'
    build_path = 'issues/index.html'
    model = Month


class MonthArchiveView(BuildableMonthArchiveView):
    model = Issue
    date_field = 'date'
    month_format = '%m'
    template_name ='browser/issue_archive_month.html'

    def get_url(self):
        return reverse(
            'archive_month',
            kwargs= {
                'month': self.month.zfill(2),
                'year': self.year
            }
        )


class IssueDetailView(BuildableDetailView):
    model = Issue
    template_name = 'browser/issue_detail.html'

    def set_kwargs(self, obj):
        super(IssueDetailView, self).set_kwargs(obj)
        self.kwargs.update(obj.date_parts_dict)

    def get_object(self):
        date_parts = map(int, [
            self.kwargs['year'],
            self.kwargs['month'],
            self.kwargs['day']
        ])
        date = datetime(*date_parts)
        try:
            return self.get_queryset().get(date=date)
        except self.get_queryset().model.DoesNotExist:
            raise Http404

    def get_url(self, obj):
        return reverse(
            'issue_detail',
            kwargs=obj.date_parts_dict
        )