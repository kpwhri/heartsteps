# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-14 00:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('activity_logs', '0002_auto_20190104_1947'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLogSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updates_log', models.BooleanField(default=True)),
                ('object_id', models.CharField(max_length=50)),
                ('activity_log', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='activity_logs.ActivityLog')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
    ]
