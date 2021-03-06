# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-05 00:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('behavioral_messages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('push_messages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContextTag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tag', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Decision',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('time', models.DateTimeField()),
                ('a_it', models.NullBooleanField()),
                ('pi_it', models.FloatField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('tags', models.ManyToManyField(to='randomization.ContextTag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('decision', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='randomization.Decision')),
                ('message_template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='behavioral_messages.MessageTemplate')),
                ('sent_message', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='push_messages.Message')),
            ],
        ),
    ]
