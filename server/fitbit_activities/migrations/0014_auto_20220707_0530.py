# Generated by Django 3.1.7 on 2022-07-07 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_activities', '0013_auto_20211014_0429'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='fitbitminuteheartrate',
            index=models.Index(fields=['account', 'time', 'heart_rate'], name='fitbit_acti_account_42c913_idx'),
        ),
    ]
