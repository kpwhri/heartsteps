# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-06-21 00:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_activities', '0003_fitbitday_wore_fitbit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitbitdailyunprocesseddata',
            name='day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unprocessed_data', to='fitbit_activities.FitbitDay'),
        ),
    ]
