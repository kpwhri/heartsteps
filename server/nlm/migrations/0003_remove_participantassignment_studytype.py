# Generated by Django 3.1.7 on 2021-04-26 20:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nlm', '0002_studytype_admins'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participantassignment',
            name='studytype',
        ),
    ]