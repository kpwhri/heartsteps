# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-02-28 00:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_activities', '0001_initial'),
        ('fitbit_activity_logs', '0002_auto_20190113_2323'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fitbitactivitytoactivitytype',
            name='fitbit_activity',
        ),
        migrations.AddField(
            model_name='fitbitactivitytoactivitytype',
            name='fitbit_activity_type',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='fitbit_activities.FitbitActivityType'),
        ),
    ]