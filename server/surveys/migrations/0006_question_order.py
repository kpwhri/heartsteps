# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-03-05 20:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0005_survey_answered'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='order',
            field=models.IntegerField(null=True),
        ),
    ]
