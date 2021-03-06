# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-04-13 21:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('uuid', models.CharField(default=uuid.uuid4, max_length=50, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('label', models.CharField(max_length=250)),
                ('description', models.CharField(blank=True, max_length=250, null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.Question')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.Survey')),
            ],
        ),
        migrations.AddField(
            model_name='surveyanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='surveys.SurveyQuestion'),
        ),
    ]
