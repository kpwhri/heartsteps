# Generated by Django 3.1.7 on 2021-07-15 22:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feature_flags', '0003_auto_20210712_1404'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='featureflags',
            name='notification_center_flag',
        ),
    ]