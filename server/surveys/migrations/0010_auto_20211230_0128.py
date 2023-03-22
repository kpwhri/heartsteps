# Generated by Django 3.1.7 on 2021-12-30 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0009_question_published'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='survey',
            index=models.Index(fields=['user', 'created'], name='surveys_sur_user_id_b53f1a_idx'),
        ),
    ]