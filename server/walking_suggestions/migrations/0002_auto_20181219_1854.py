# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-12-19 18:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('walking_suggestions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuration',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]
