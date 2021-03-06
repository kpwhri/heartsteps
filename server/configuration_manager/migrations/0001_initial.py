# Generated by Django 3.1.7 on 2021-07-02 21:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_str', models.CharField(max_length=512)),
                ('attr', models.JSONField(null=True)),
                ('value', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='QueryString',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_str', models.CharField(max_length=512, unique=True)),
                ('level', models.IntegerField(default=0)),
                ('when_created', models.DateTimeField(auto_now_add=True)),
                ('who_created', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='configuration',
            index=models.Index(fields=['query_str'], name='configurati_query_s_3cdbdf_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='configuration',
            unique_together={('query_str', 'attr')},
        ),
        migrations.AddIndex(
            model_name='querystring',
            index=models.Index(fields=['query_str'], name='configurati_query_s_2d0a81_idx'),
        ),
    ]
