# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-09 20:20
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_api', '0002_auto_20180925_1700'),
    ]

    operations = [
        migrations.CreateModel(
            name='FitbitSubscriptionUpdate',
            fields=[
                ('uuid', models.CharField(default=uuid.uuid4, max_length=50, primary_key=True, serialize=False)),
                ('payload', django.contrib.postgres.fields.jsonb.JSONField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fitbit_api.FitbitSubscription')),
            ],
        ),
    ]
