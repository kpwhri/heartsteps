# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-01-04 21:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_api', '0047_fitbitdeviceupdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fitbitdevice',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='fitbit_api.FitbitAccount'),
        ),
    ]
