# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-10 01:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_api', '0005_auto_20181010_0039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitbitaccount',
            name='access_token',
            field=models.TextField(blank=True, help_text='The OAuth2 access token', null=True),
        ),
        migrations.AlterField(
            model_name='fitbitaccount',
            name='expires_at',
            field=models.FloatField(blank=True, help_text='The timestamp when the access token expires', null=True),
        ),
        migrations.AlterField(
            model_name='fitbitaccount',
            name='refresh_token',
            field=models.TextField(blank=True, help_text='The OAuth2 refresh token', null=True),
        ),
    ]
