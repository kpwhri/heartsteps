# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-05-07 14:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_requests', '0007_auto_20190624_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='request_time',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
