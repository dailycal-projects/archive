from django.contrib import admin
from archive.models import Page, Issue


class PageAdmin(admin.ModelAdmin):
    pass

class IssueAdmin(admin.ModelAdmin):
    pass

admin.site.register(Page, PageAdmin)
admin.site.register(Issue, IssueAdmin)