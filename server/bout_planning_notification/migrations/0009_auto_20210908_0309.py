# Generated by Django 3.1.7 on 2021-09-08 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bout_planning_notification', '0008_auto_20210908_0300'),
    ]

    operations = [
        migrations.AddField(
            model_name='boutplanningdecision',
            name='N',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='boutplanningdecision',
            name='O',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='boutplanningdecision',
            name='R',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='level',
            name='level',
            field=models.CharField(choices=[('RE', 'RE'), ('RA', 'RA'), ('NO', 'NO'), ('NR', 'NR'), ('FU', 'FU')], max_length=20),
        ),
    ]
