# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-05-07 15:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_requests', '0008_auto_20200507_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicerequest',
            name='request_time',
            field=models.DateTimeField(db_index=True, editable=False),
        ),
    ]
