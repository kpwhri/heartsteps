# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-07-06 22:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('daily_tasks', '0003_dailytask_day'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('adherence_messages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=True)),
                ('daily_task', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='daily_tasks.DailyTask')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='dailyadherencemetric',
            name='day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='days.Day'),
        ),
        migrations.AlterField(
            model_name='dailyadherencemetric',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
