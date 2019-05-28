# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-05-27 22:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('days', '0002_auto_20190527_2113'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='day',
            options={'ordering': ['date']},
        ),
        migrations.AlterUniqueTogether(
            name='day',
            unique_together=set([('user', 'date')]),
        ),
    ]