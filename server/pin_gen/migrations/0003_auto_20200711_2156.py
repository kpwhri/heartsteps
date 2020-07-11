# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-07-11 21:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pin_gen', '0002_auto_20200710_1551'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Customer',
        ),
        migrations.AddField(
            model_name='pin',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pin',
            name='pin_digits',
            field=models.IntegerField(null=True),
        ),
    ]
