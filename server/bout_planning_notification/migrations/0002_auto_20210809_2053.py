# Generated by Django 3.1.7 on 2021-08-09 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bout_planning_notification', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='firstboutplanningtime',
            name='time',
        ),
        migrations.AddField(
            model_name='firstboutplanningtime',
            name='hour',
            field=models.IntegerField(default=7),
        ),
        migrations.AddField(
            model_name='firstboutplanningtime',
            name='minute',
            field=models.IntegerField(default=0),
        ),
    ]
