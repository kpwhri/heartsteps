# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-05-31 16:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('push_messages', '0006_auto_20190531_1629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='text',
            new_name='body',
        ),
    ]