# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-08-21 18:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('weeks', '0007_auto_20190821_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklybarrieroption',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]