# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-01-02 21:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0011_auto_20191014_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]