# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-07-07 01:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adherence_messages', '0002_auto_20190706_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='hour',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='configuration',
            name='minute',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
