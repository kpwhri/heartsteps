# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-05-08 02:18
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('walking_suggestions', '0010_auto_20190508_0203'),
    ]

    operations = [
        migrations.AddField(
            model_name='nightlyupdate',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2019, 5, 8, 2, 18, 48, 231453, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='nightlyupdate',
            name='updated_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
