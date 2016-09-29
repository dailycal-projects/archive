from datetime import datetime
from django.shortcuts import render
from django.views.generic.dates import DateDetailView
from django.views.generic.detail import DetailView
from archive.models import Issue

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