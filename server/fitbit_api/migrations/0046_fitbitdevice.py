# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2020-01-04 19:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_api', '0045_auto_20190929_2302'),
    ]

    operations = [
        migrations.CreateModel(
            name='FitbitDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fitbit_id', models.CharField(max_length=125)),
                ('mac', models.CharField(max_length=125)),
                ('device_type', models.CharField(max_length=125)),
                ('device_version', models.CharField(max_length=125)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='fitbit_api.FitbitAccountUpdate')),
            ],
        ),
    ]
