# Generated by Django 3.1.7 on 2021-09-08 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bout_planning_notification', '0009_auto_20210908_0309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='randomdecision',
            name='random_value',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
