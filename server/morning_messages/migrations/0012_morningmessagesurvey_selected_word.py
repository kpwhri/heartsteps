# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-05-05 22:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('morning_messages', '0011_morningmessagesurvey_word_set_string'),
    ]

    operations = [
        migrations.AddField(
            model_name='morningmessagesurvey',
            name='selected_word',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
