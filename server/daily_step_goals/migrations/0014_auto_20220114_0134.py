# Generated by Django 3.1.7 on 2022-01-14 01:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0025_auto_20210909_0131'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('daily_step_goals', '0013_auto_20220113_0633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stepgoalsequence_user',
            name='step_goal_sequence',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='daily_step_goals.stepgoalsequence'),
        ),
        migrations.AlterField(
            model_name='stepgoalsequence_user',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='stepgoalsequenceblock',
            name='cohort',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='participants.cohort'),
        ),
    ]