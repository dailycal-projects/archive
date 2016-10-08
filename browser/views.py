import random
import calendar
from django.urls import reverse
from datetime import datetime
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.dates import DateDetailView
from django.views.generic.detail import DetailView


from archive.models import Issue, Page

class HomeView(TemplateView):
    template_name = 'browser/home.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(HomeView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the issues
        context['issue_count'] = Issue.objects.count()
        context['page_count'] = Page.objects.count()

        random_index = random.randint(0, context['issue_count'] - 1)
        random_issue = Page.objects.all()[random_index]
        context['random_issue_url'] = reverse('issue_detail', args=[random_issue.date.year, format(random_issue.date,'%m'), format(random_issue.date,'%d')])

        return context


class SponsorView(TemplateView):
    template_name = 'browser/sponsor.html'


class AboutView(TemplateView):
    template_name = 'browser/about.html'


class MonthListView(TemplateView):
    template_name = 'browser/issue_archive.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MonthListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the issues
        date_list = Issue.objects.values_list('date', flat=True)
        month_list = [(date.year, date.month) for date in date_list]
        months_completed = list(set(month_list))

        context['years'] = {}
        for year in range(1871,2010):
            context['years'][str(year)] = []
            for month in range(1,13):
                if (year, month) in months_completed:
                    url = reverse('archive_month', args=[year, format(month, '02d')])
                else:
                    url = None
                context['years'][str(year)].append((calendar.month_abbr[month], url))

        return context


class IssueDetailView(DetailView):

    model = Issue
    date_field="date"
    template_name = 'browser/issue_detail.html'

    def set_kwargs(self, obj):
        super(IssueDetailView, self).set_kwargs(obj)
        self.kwargs.update({
            'year': obj.date.year,
            'month': dateformat(obj.date, 'm'),
            'day': dateformat(obj.date, 'd'),
        })

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
            kwargs=dict(
                year=obj.date.year,
                month=dateformat(obj.date, 'm'),
                day=dateformat(obj.date, 'd'),
            )
        )