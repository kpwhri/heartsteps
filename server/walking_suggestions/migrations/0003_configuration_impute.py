# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-10 19:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walking_suggestions', '0002_auto_20181219_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='impute',
            field=models.BooleanField(default=False),
        ),
    ]
