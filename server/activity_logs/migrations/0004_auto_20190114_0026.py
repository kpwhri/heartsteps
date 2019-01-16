# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-14 00:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('activity_logs', '0003_activitylogsource'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitylogsource',
            name='updates_log',
        ),
        migrations.AddField(
            model_name='activitylogsource',
            name='updated_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]