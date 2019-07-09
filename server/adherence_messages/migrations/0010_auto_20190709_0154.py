# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-07-09 01:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adherence_messages', '0009_adherencemessage_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyadherencemetric',
            name='category',
            field=models.CharField(choices=[('wore-fitbit', 'Wore fitbit'), ('app-used', 'Used app'), ('app-installed', 'Installed app')], max_length=70),
        ),
    ]
