# Generated by Django 3.1.7 on 2021-07-15 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_flags', '0004_remove_featureflags_notification_center_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='featureflags',
            name='flags',
            field=models.TextField(default=''),
        ),
    ]
