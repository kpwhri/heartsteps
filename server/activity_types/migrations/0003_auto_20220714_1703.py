# Generated by Django 3.1.7 on 2022-07-14 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_types', '0002_auto_20200822_2308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitytype',
            name='name',
            field=models.CharField(max_length=500, unique=True),
        ),
        migrations.AlterField(
            model_name='activitytype',
            name='title',
            field=models.CharField(max_length=500),
        ),
    ]
