# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-10-29 18:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0005_auto_20161026_1934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='month',
            name='available',
        ),
    ]
