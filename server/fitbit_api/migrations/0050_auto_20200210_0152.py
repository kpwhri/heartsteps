# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-02-10 01:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_api', '0049_auto_20200210_0132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitbitdeviceupdate',
            name='battery_level',
            field=models.IntegerField(null=True),
        ),
    ]
