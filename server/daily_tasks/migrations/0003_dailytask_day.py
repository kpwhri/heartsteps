# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-12-27 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daily_tasks', '0002_auto_20181219_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailytask',
            name='day',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
