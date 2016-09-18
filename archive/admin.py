from django.contrib import admin
from archive.models import Page

class PageAdmin(admin.ModelAdmin):
    pass
admin.site.register(Page, PageAdmin)