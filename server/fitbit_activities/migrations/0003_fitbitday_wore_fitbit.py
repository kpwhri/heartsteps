# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-06-03 19:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_activities', '0002_fitbitminuteheartrate'),
    ]

    operations = [
        migrations.AddField(
            model_name='fitbitday',
            name='wore_fitbit',
            field=models.BooleanField(default=False),
        ),
    ]