# Generated by Django 3.1.7 on 2021-03-01 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('daily_tasks', '0003_dailytask_day'),
        ('weekly_reflection', '0004_auto_20190304_0237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reflectiontime',
            name='daily_task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='daily_tasks.dailytask'),
        ),
    ]