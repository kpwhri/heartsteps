# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-08-22 23:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_types', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitytype',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
