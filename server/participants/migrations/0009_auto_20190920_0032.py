# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-09-20 00:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('participants', '0008_auto_20190902_1902'),
    ]

    operations = [
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75, unique=True)),
                ('contact_number', models.CharField(max_length=12, null=True)),
                ('admins', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='cohort',
            name='study',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='participants.Study'),
        ),
    ]
