# Generated by Django 3.1.7 on 2021-12-17 06:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('daily_step_goals', '0009_auto_20211217_0629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stepgoalsevidence',
            old_name='median',
            new_name='base',
        ),
    ]
