# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-04-14 01:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0004_auto_20190413_2320'),
        ('weeks', '0005_auto_20190306_2017'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeekQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='surveys.Question')),
            ],
            bases=('surveys.question',),
        ),
        migrations.CreateModel(
            name='WeekSurvey',
            fields=[
                ('survey_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='surveys.Survey')),
            ],
            bases=('surveys.survey',),
        ),
        migrations.AddField(
            model_name='week',
            name='survey',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='weeks.WeekSurvey'),
        ),
    ]