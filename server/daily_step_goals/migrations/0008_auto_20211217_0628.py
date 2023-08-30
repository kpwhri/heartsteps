# Generated by Django 3.1.7 on 2021-12-17 06:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0025_auto_20210909_0131'),
        ('daily_step_goals', '0007_stepgoalcalculationsettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stepgoalcalculationsettings',
            name='cohort',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='participants.cohort', unique=True),
        ),
    ]