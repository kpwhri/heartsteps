# Generated by Django 3.1.7 on 2021-03-06 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push_messages', '0009_message_collapse_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='data',
            field=models.JSONField(null=True),
        ),
    ]