# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-15 00:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_api', '0024_auto_20190115_0024'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fitbitday',
            options={'ordering': ['date']},
        ),
    ]
