# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-07-27 19:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0013_dataexport'),
    ]

    operations = [
        migrations.AddField(
            model_name='cohort',
            name='study_length',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
