# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-29 22:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_summaries', '0002_day_total_minutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='day',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
