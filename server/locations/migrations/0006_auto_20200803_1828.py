# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-08-03 18:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0005_location_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='source',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
