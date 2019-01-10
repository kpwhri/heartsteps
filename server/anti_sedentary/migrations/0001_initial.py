# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-10 18:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('randomization', '0008_decision_test'),
        ('behavioral_messages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AntiSedentaryDecision',
            fields=[
                ('decision_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='randomization.Decision')),
            ],
            bases=('randomization.decision',),
        ),
        migrations.CreateModel(
            name='AntiSedentaryMessageTemplate',
            fields=[
                ('messagetemplate_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='behavioral_messages.MessageTemplate')),
            ],
            bases=('behavioral_messages.messagetemplate',),
        ),
    ]
