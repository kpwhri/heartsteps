# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-10-01 01:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_surveys', '0005_auto_20200325_0124'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='treatment_probability',
            field=models.FloatField(null=True),
        ),
    ]
