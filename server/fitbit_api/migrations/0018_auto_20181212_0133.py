# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-12-12 01:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fitbit_api', '0017_fitbitsubscriptionupdate_update'),
    ]

    operations = [
        migrations.CreateModel(
            name='FitbitAccountUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='fitbitaccount',
            name='user',
        ),
        migrations.AddField(
            model_name='fitbitaccountuser',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fitbit_api.FitbitAccount'),
        ),
        migrations.AddField(
            model_name='fitbitaccountuser',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
