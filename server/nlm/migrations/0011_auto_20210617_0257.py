# Generated by Django 3.1.7 on 2021-06-17 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nlm', '0010_auto_20210617_0247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logcontents',
            name='value',
            field=models.TextField(blank=True, null=True),
        ),
    ]