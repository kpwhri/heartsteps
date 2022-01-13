# Generated by Django 3.1.7 on 2022-01-13 06:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('participants', '0025_auto_20210909_0131'),
        ('daily_step_goals', '0012_stepgoal_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='StepGoalSequence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(null=True)),
                ('is_used', models.BooleanField(default=False)),
                ('when_created', models.DateTimeField(auto_now_add=True)),
                ('when_used', models.DateTimeField(default=None, null=True)),
                ('sequence_text', models.TextField(default='0.3,0.4,0.5,0.6,0.7,0.8,0.9')),
                ('cohort', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='participants.cohort')),
            ],
        ),
        migrations.CreateModel(
            name='StepGoalSequence_User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned', models.DateTimeField(auto_now_add=True)),
                ('step_goal_sequence', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='daily_step_goals.stepgoalsequence')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StepGoalSequenceBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seq_block', models.TextField(default=None, null=True)),
                ('when_created', models.DateTimeField(auto_now_add=True)),
                ('when_used', models.DateTimeField(default=None, null=True)),
                ('cohort', models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='participants.cohort')),
            ],
        ),
        migrations.DeleteModel(
            name='StepGoalPRBScsv',
        ),
    ]
