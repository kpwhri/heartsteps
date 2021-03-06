# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-07-06 22:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('days', '0003_auto_20190527_2251'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyAdherenceMetric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('wore-fitbit', 'Wore fitbit'), ('used-app', 'Used app')], max_length=70)),
                ('value', models.BooleanField(default=False)),
                ('day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adherence_metrics', to='days.Day')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adherence_metrics', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
