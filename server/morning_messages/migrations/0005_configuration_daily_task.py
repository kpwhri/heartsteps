# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-12-19 19:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('daily_tasks', '0002_auto_20181219_1859'),
        ('morning_messages', '0004_configuration'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='daily_task',
            field=models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='morning_message_configuration', to='daily_tasks.DailyTask'),
        ),
    ]
