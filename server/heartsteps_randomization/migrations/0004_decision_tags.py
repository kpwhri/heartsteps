# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-29 21:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heartsteps_messages', '0004_auto_20180717_1647'),
        ('heartsteps_randomization', '0003_auto_20180725_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='decision',
            name='tags',
            field=models.ManyToManyField(to='heartsteps_messages.ContextTag'),
        ),
    ]
