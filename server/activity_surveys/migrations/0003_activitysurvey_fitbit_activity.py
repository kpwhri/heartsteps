# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-03-05 19:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_activities', '0004_auto_20190621_0012'),
        ('activity_surveys', '0002_activitysurveyquestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitysurvey',
            name='fitbit_activity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='fitbit_activities.FitbitActivity'),
        ),
    ]
