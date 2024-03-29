# Generated by Django 3.1.7 on 2022-04-22 19:40

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_auto_20211229_0115'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportRecipients',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('recipient_email', models.TextField(blank=True)),
                ('report_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reports.reporttype')),
            ],
        ),
    ]
