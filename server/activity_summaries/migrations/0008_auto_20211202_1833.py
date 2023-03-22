# Generated by Django 3.1.7 on 2021-12-02 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_summaries', '0007_auto_20210331_1910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='activities_completed',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='day',
            name='miles',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='day',
            name='steps',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='day',
            name='total_minutes',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]