# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-08-27 19:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('randomization', '0016_auto_20190821_1743'),
    ]

    operations = [
        migrations.CreateModel(
            name='DecisionRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked', models.NullBooleanField()),
                ('comments', models.CharField(max_length=250, null=True)),
                ('decision', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='randomization.Decision')),
            ],
        ),
    ]
