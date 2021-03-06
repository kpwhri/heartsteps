# Generated by Django 3.1.7 on 2021-03-01 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('morning_messages', '0013_morningmessagecontextobject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='morningmessage',
            name='message_decision',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='morning_messages.morningmessagedecision'),
        ),
        migrations.AlterField(
            model_name='morningmessage',
            name='survey',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='morning_messages.morningmessagesurvey'),
        ),
    ]
