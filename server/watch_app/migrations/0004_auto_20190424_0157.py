# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-04-24 01:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('watch_app', '0003_auto_20190422_1949'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stepcount',
            options={'ordering': ['start']},
        ),
        migrations.RenameField(
            model_name='stepcount',
            old_name='step_dtm',
            new_name='end',
        ),
        migrations.RemoveField(
            model_name='stepcount',
            name='step_number',
        ),
        migrations.AddField(
            model_name='stepcount',
            name='start',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stepcount',
            name='steps',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stepcount',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]