# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-01-12 22:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('randomization', '0009_decision_available'),
    ]

    operations = [
        migrations.RenameField(
            model_name='decision',
            old_name='a_it',
            new_name='treated',
        ),
        migrations.RenameField(
            model_name='decision',
            old_name='pi_it',
            new_name='treatment_probability',
        ),
    ]
