# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-07-10 18:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('randomization', '0013_auto_20190710_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='available',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='decision',
            name='sedentary',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='unavailablereason',
            name='reason',
            field=models.CharField(choices=[('unreachable', 'Unreachable'), ('notification-recently-sent', 'Notification recently sent'), ('not-sedentary', 'Not sedentary'), ('on-vacation', 'On vaaction'), ('disabled', 'Disabled')], max_length=150),
        ),
    ]