# Generated by Django 3.1.7 on 2021-12-22 04:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bout_planning_notification', '0022_remove_levelsequence_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='LevelSequence_User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_sequence', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='bout_planning_notification.levelsequence')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
