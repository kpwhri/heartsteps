# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-04-15 20:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push_messages', '0004_auto_20190413_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='external_id',
            field=models.CharField(max_length=150, null=True),
        ),
    ]