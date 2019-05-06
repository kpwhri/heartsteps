# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-03-04 02:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_plans', '0003_auto_20190112_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityplan',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='activityplan',
            name='timeOfDay',
            field=models.CharField(choices=[('morning', 'Morning'), ('lunch', 'Lunch'), ('midafternoon', 'Afternoon'), ('evening', 'Evening'), ('postdinner', 'Post dinner')], max_length=20, null=True),
        ),
    ]
